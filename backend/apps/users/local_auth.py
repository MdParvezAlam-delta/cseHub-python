from datetime import timedelta
from uuid import uuid4

import jwt
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.http import Http404
from django.utils import timezone
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserProfileSerializer
from .authentication import LocalPasswordJWTAuthentication, SupabaseJWTAuthentication

LOCAL_ISSUER = f'{settings.SUPABASE_URL}/local-auth'
LOCAL_AUDIENCE = 'csehub-local'


def create_access_token(user):
    now = timezone.now()
    return jwt.encode(
        {
            'sub': str(user.pk),
            'iss': LOCAL_ISSUER,
            'aud': LOCAL_AUDIENCE,
            'iat': now,
            'exp': now + timedelta(hours=12),
        },
        settings.SECRET_KEY,
        algorithm='HS256',
    )


class LocalSignupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, trim_whitespace=True)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters.')
        return value.strip()

    def validate_email(self, value):
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return email

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=f'local_{uuid4().hex}',
            display_name=validated_data['name'],
        )
        user.set_password(validated_data['password'])
        try:
            with transaction.atomic():
                user.save()
        except IntegrityError as exc:
            raise serializers.ValidationError(
                {'email': 'An account with this email already exists.'}
            ) from exc
        return user


class LocalSigninSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        email = attrs['email'].strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if not user or not user.has_usable_password() or not user.check_password(attrs['password']):
            raise serializers.ValidationError('Invalid email or password.')
        if not user.is_active:
            raise serializers.ValidationError('This account is disabled.')
        attrs['user'] = user
        return attrs


class LocalAuthView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def initial(self, request, *args, **kwargs):
        if not settings.LOCAL_AUTH_ENABLED:
            raise Http404
        return super().initial(request, *args, **kwargs)

    @staticmethod
    def response_for(user, status_code=200):
        return Response(
            {'access_token': create_access_token(user), 'user': UserProfileSerializer(user).data},
            status=status_code,
        )


class LocalSignupView(LocalAuthView):
    def post(self, request):
        serializer = LocalSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.response_for(serializer.save(), status_code=201)


class LocalSigninView(LocalAuthView):
    def post(self, request):
        serializer = LocalSigninSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.response_for(serializer.validated_data['user'])


class LocalMeView(LocalAuthView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [
        LocalPasswordJWTAuthentication,
        SupabaseJWTAuthentication,
    ]

    def get(self, request):
        return Response(UserProfileSerializer(request.user).data)
