import logging
import jwt
from jwt import PyJWKClient, PyJWTError
from django.conf import settings
from django.db import IntegrityError, transaction
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.users.models import User

logger = logging.getLogger(__name__)

ISSUER = f"{settings.SUPABASE_URL}/auth/v1"
# One shared client: caches the key set instead of fetching per request.
_jwks = PyJWKClient(f"{ISSUER}/.well-known/jwks.json",
                    cache_keys=True, lifespan=3600, timeout=5)


class SupabaseJWTAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        return "Bearer"          # makes DRF return 401, not 403

    def authenticate(self, request):
        header = request.headers.get("Authorization")
        if not header:
            return None
        parts = header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        token = parts[1]

        try:
            alg = jwt.get_unverified_header(token).get("alg")
            if alg == "HS256":                       # legacy Supabase projects
                key = settings.SUPABASE_JWT_SECRET
            else:                                    # ES256 / RS256 via JWKS
                key = _jwks.get_signing_key_from_jwt(token).key
            payload = jwt.decode(
                token, key,
                algorithms=["HS256", "ES256", "RS256"],
                audience="authenticated", issuer=ISSUER,
            )
        except PyJWTError as exc:
            logger.info("JWT rejected: %s", exc)     # log detail, don't return it
            raise AuthenticationFailed("Invalid or expired token.")

        user = self._get_or_create_user(payload)
        if not user.is_active:
            raise AuthenticationFailed("Account disabled.")
        return (user, token)

    @staticmethod
    def _get_or_create_user(payload):
        uid = payload.get("sub")
        if not uid:
            raise AuthenticationFailed("Invalid token.")

        user = User.objects.filter(supabase_uid=uid).first()
        if user:
            return user

        email = (payload.get("email") or "").lower()
        if not email:
            raise AuthenticationFailed("Token has no email.")
        metadata = payload.get("user_metadata") or {}

        # Link a pre-existing Django-only account (e.g. your admin superuser)
        # but only if Supabase says the email is verified.
        existing = User.objects.filter(
            email__iexact=email, supabase_uid__isnull=True).first()
        if existing and metadata.get("email_verified"):
            existing.supabase_uid = uid
            existing.save(update_fields=["supabase_uid"])
            return existing

        display_name = metadata.get("display_name") or metadata.get("full_name") or ""
        user = User(
            supabase_uid=uid,
            email=email,
            username=f"{email.split('@')[0][:100]}_{uid[:8]}",
            display_name=display_name[:100],
        )
        user.set_unusable_password()
        try:
            with transaction.atomic():
                user.save()
        except IntegrityError:        # concurrent first request, or email taken
            user = User.objects.filter(supabase_uid=uid).first()
            if not user:
                raise AuthenticationFailed("Account conflict.")
        return user


class LocalPasswordJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if not settings.LOCAL_AUTH_ENABLED:
            return None

        parts = request.headers.get("Authorization", "").split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None

        token = parts[1]
        try:
            unverified = jwt.decode(
                token,
                options={"verify_signature": False, "verify_exp": False},
            )
            issuer = f"{settings.SUPABASE_URL}/local-auth"
            if unverified.get("iss") != issuer:
                return None

            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
                audience="csehub-local",
                issuer=issuer,
            )
            user = User.objects.get(pk=payload["sub"], is_active=True)
        except (PyJWTError, User.DoesNotExist, KeyError, ValueError) as exc:
            raise AuthenticationFailed("Invalid or expired token.") from exc
        return (user, token)

