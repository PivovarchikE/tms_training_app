import secrets

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers

from .models import DiaryEntry, User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_trainer",
            "role",
            "bio",
            "phone",
            "email_verified",
            "date_of_birth",
            "full_name",
            "created_at",
            "updated_at",
            "avatar",
        ]
        read_only_fields = ["email_verified", "created_at", "updated_at"]


# ==================== Registration Serializers ====================


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "is_trainer",
        ]

    def validate_email(self, value):
        """Check if email is already registered."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("User with this email already exists.")
        return value.lower()

    def validate_username(self, value):
        """Check if username is already taken."""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_password(self, value):
        """Validate password using Django's password validators."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Check that passwords match."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create user with hashed password and verification token."""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        # Generate email verification token
        verification_token = secrets.token_urlsafe(32)

        user = User(
            **validated_data,
            email_verification_token=verification_token,
            email_verification_sent_at=timezone.now(),
        )
        user.set_password(password)
        user.save()

        return user


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for email verification."""

    token = serializers.CharField(max_length=100)

    def validate_token(self, value):
        """Validate the verification token."""
        try:
            user = User.objects.get(email_verification_token=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired verification token.")

        if user.email_verified:
            raise serializers.ValidationError("Email is already verified.")

        # Check token expiration (24 hours)
        if user.email_verification_sent_at:
            expiration_time = user.email_verification_sent_at + timezone.timedelta(
                hours=24
            )
            if timezone.now() > expiration_time:
                raise serializers.ValidationError("Verification token has expired.")

        self.user = user
        return value

    def save(self):
        """Mark email as verified."""
        self.user.email_verified = True
        self.user.email_verification_token = None
        self.user.save(update_fields=["email_verified", "email_verification_token"])
        return self.user


class ResendVerificationSerializer(serializers.Serializer):
    """Serializer for resending verification email."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Check if user exists and email is not verified."""
        try:
            user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if user.email_verified:
            raise serializers.ValidationError("Email is already verified.")

        self.user = user
        return value

    def save(self):
        """Generate new verification token."""
        self.user.email_verification_token = secrets.token_urlsafe(32)
        self.user.email_verification_sent_at = timezone.now()
        self.user.save(
            update_fields=["email_verification_token", "email_verification_sent_at"]
        )
        return self.user


# ==================== Login Serializers ====================


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        """Authenticate user."""
        username = attrs.get("username")
        password = attrs.get("password")

        # Try to authenticate with username or email
        user = authenticate(username=username, password=password)

        if not user:
            # Try email login
            try:
                user_by_email = User.objects.get(email__iexact=username)
                user = authenticate(username=user_by_email.username, password=password)
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError(
                {"detail": "Invalid credentials. Please try again."}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "This account has been deactivated."}
            )

        attrs["user"] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password."""

    old_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate_old_password(self, value):
        """Check old password is correct."""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        """Validate new password."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Check new passwords match."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "New passwords do not match."}
            )
        return attrs

    def save(self):
        """Update user password."""
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Check if user exists."""
        try:
            self.user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            # Don't reveal if email exists
            pass
        return value

    def save(self):
        """Generate password reset token."""
        if hasattr(self, "user"):
            self.user.email_verification_token = secrets.token_urlsafe(32)
            self.user.email_verification_sent_at = timezone.now()
            self.user.save(
                update_fields=["email_verification_token", "email_verification_sent_at"]
            )
            return self.user
        return None


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset."""

    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
    )
    new_password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
    )

    def validate_token(self, value):
        """Validate the reset token."""
        try:
            user = User.objects.get(email_verification_token=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired reset token.")

        # Check token expiration (1 hour for password reset)
        if user.email_verification_sent_at:
            expiration_time = user.email_verification_sent_at + timezone.timedelta(
                hours=1
            )
            if timezone.now() > expiration_time:
                raise serializers.ValidationError("Reset token has expired.")

        self.user = user
        return value

    def validate_new_password(self, value):
        """Validate new password."""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Check new passwords match."""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": "Passwords do not match."}
            )
        return attrs

    def save(self):
        """Reset user password."""
        self.user.set_password(self.validated_data["new_password"])
        self.user.email_verification_token = None
        self.user.save(update_fields=["password", "email_verification_token"])
        return self.user


# ==================== Legacy Serializers ====================


class UserCreateSerializer(RegisterSerializer):
    """Alias for RegisterSerializer for backwards compatibility."""

    pass


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "bio",
            "phone",
            "date_of_birth",
            "avatar",
        ]


class TrainerSerializer(serializers.ModelSerializer):
    """Serializer for Trainer users (public profile)."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "bio",
            "full_name",
        ]


# ==================== Diary Serializers ====================


class DiaryEntrySerializer(serializers.ModelSerializer):
    """Serializer for DiaryEntry model."""

    class Meta:
        model = DiaryEntry
        fields = [
            "id",
            "user",
            "title",
            "content",
            "mood",
            "workout",
            "is_private",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]


class DiaryEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a DiaryEntry."""

    class Meta:
        model = DiaryEntry
        fields = [
            "title",
            "content",
            "mood",
            "workout",
            "is_private",
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
