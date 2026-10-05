from django.urls import path

from .local_auth import LocalMeView, LocalSigninView, LocalSignupView

urlpatterns = [
    path('signup/', LocalSignupView.as_view(), name='local-signup'),
    path('signin/', LocalSigninView.as_view(), name='local-signin'),
    path('me/', LocalMeView.as_view(), name='local-me'),
]
