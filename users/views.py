from django.contrib.auth import logout
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from providers.keys import KeyGenerator
from providers.redis_provider import Redis

from .models import DiaryEntry, User
from .serializers import (
    ChangePasswordSerializer,
    DiaryEntryCreateSerializer,
    DiaryEntrySerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    RegisterSerializer,
    ResendVerificationSerializer,
    TrainerSerializer,
    UserSerializer,
    UserUpdateSerializer,
    VerifyEmailSerializer,
)

redis_cache = Redis()
key_gen = KeyGenerator(KeyGenerator.USER)


# ==================== Auth Views ====================


class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.

    POST /api/auth/register/

    Creates a new user account and returns JWT tokens.
    """

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        from users.tasks import send_verification_email
        send_verification_email.delay(user.id)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Registration successful. Please verify your email.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                "verification_token": user.email_verification_token,  # For development
            },
            status=status.HTTP_201_CREATED,
        )


class ResendVerificationView(APIView):
    """
    Resend verification email endpoint.

    POST /api/auth/resend-verification/
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        from users.tasks import send_verification_email
        send_verification_email.delay(user.id)

        return Response(
            {"message": "Verification email sent. Please check your inbox."},
                status=status.HTTP_200_OK
        )

class LoginView(APIView):
    """
    User login endpoint.

    POST /api/auth/login/

    Authenticates user and returns JWT tokens.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful.",
                "user": UserSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    User logout endpoint.

    POST /api/auth/logout/

    Blacklists the refresh token.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            logout(request)

            return Response(
                {"message": "Logout successful."},
                status=status.HTTP_200_OK,
            )
        except Exception:
            return Response(
                {"message": "Logout successful."},
                status=status.HTTP_200_OK,
            )


class VerifyEmailView(APIView):
    """
    Email verification endpoint.

    POST /api/auth/verify-email/

    Verifies user's email address using the verification token.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "Email verified successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class ResendVerificationView(APIView):
    """
    Resend verification email endpoint.

    POST /api/auth/resend-verification/

    Generates a new verification token and sends email.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResendVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # TODO: Send verification email via Celery task

        return Response(
            {
                "message": "Verification email sent.",
                "verification_token": user.email_verification_token,  # For development
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    """
    Change password endpoint.

    POST /api/auth/change-password/

    Changes the authenticated user's password.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class PasswordResetRequestView(APIView):
    """
    Request password reset endpoint.

    POST /api/auth/password-reset/

    Sends password reset email.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # TODO: Send password reset email via Celery task

        response_data = {
            "message": "If an account exists with this email, a reset link has been sent.",
        }

        # For development: include token
        if user:
            response_data["reset_token"] = user.email_verification_token

        return Response(response_data, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """
    Confirm password reset endpoint.

    POST /api/auth/password-reset/confirm/

    Resets user's password using the reset token.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Password reset successful. You can now login with your new password."
            },
            status=status.HTTP_200_OK,
        )


# ==================== User Views ====================


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model.

    Endpoints:
    - GET /users/ - list all users (admin only)
    - GET /users/{id}/ - retrieve user
    - PUT/PATCH /users/{id}/ - update user (owner or admin)
    - DELETE /users/{id}/ - delete user (admin only)
    - GET /users/me/ - get current user profile
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["list", "destroy"]:
            # return [permissions.IsAdminUser()]
            return [permissions.BasePermission()]
        return [permissions.BasePermission()]
        # return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        return User.objects.all()
        # if self.request.user.is_staff:
        #     return User.objects.all()
        # # Regular users can only see their own profile
        # return User.objects.filter(pk=self.request.user.pk)

    @action(detail=False, methods=["get", "put", "patch"])
    def me(self, request):
        """Get or update current user's profile."""
        user = request.user

        if request.method == "GET":
            serializer = UserSerializer(user)
            return Response(serializer.data)

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserSerializer(user).data)

    # Кэширование включено, 20 минут, используется декоратор
    # @method_decorator(cache_page(60*20))
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        cache_key = key_gen.standard_many()
        cache_data = redis_cache.get(cache_key)

        if cache_data:
            return Response(cache_data)

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        redis_cache.set(cache_key, data)

        return Response(data)

    def retrieve(self, request, *args, **kwargs):
        cache_key = key_gen.standard_one(kwargs["pk"])
        cache_data = redis_cache.get(cache_key)

        if cache_data:
            return Response(cache_data)

        response = super().retrieve(request, *args, **kwargs)
        redis_cache.set(cache_key, response.data)

        return super().retrieve(request, *args, **kwargs)


class TrainerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for listing trainers (public).

    Endpoints:
    - GET /trainers/ - list all trainers
    - GET /trainers/{id}/ - retrieve trainer profile
    """

    queryset = User.objects.filter(is_trainer=True)
    serializer_class = TrainerSerializer
    permission_classes = [permissions.AllowAny]


class DiaryEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DiaryEntry model.

    Endpoints:
    - GET /diary/ - list user's diary entries
    - POST /diary/ - create new diary entry
    - GET /diary/{id}/ - retrieve diary entry
    - PUT/PATCH /diary/{id}/ - update diary entry
    - DELETE /diary/{id}/ - delete diary entry
    """

    serializer_class = DiaryEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DiaryEntry.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return DiaryEntryCreateSerializer
        return DiaryEntrySerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
