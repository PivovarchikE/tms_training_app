from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

import config.settings as settings

from .views import (
    ChangePasswordView,
    DiaryEntryViewSet,
    LoginView,
    LogoutView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    RegisterView,
    ResendVerificationView,
    TrainerViewSet,
    UserViewSet,
    VerifyEmailView,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"trainers", TrainerViewSet, basename="trainer")
router.register(r"diary", DiaryEntryViewSet, basename="diary")

# Auth URLs
auth_urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify_email"),
    path(
        "resend-verification/",
        ResendVerificationView.as_view(),
        name="resend_verification",
    ),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path(
        "password-reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include((auth_urlpatterns, "auth"))),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__", include(debug_toolbar.urls)),
    ] + urlpatterns
