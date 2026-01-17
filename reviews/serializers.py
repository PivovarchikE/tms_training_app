from rest_framework import serializers

from .models import Review, TrainerReview


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for Review model."""

    class Meta:
        model = Review
        fields = [
            "id",
            "plan",
            "user",
            "rating",
            "title",
            "text",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "is_approved", "created_at", "updated_at"]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Review."""

    class Meta:
        model = Review
        fields = [
            "plan",
            "rating",
            "title",
            "text",
        ]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        plan = attrs.get("plan")

        # User cannot review their own plan
        if plan and plan.trainer == user:
            raise serializers.ValidationError(
                {"plan": "You cannot review your own training plan."}
            )

        # Check if user already reviewed this plan
        if Review.objects.filter(plan=plan, user=user).exists():
            raise serializers.ValidationError(
                {"plan": "You have already reviewed this plan."}
            )

        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class TrainerReviewSerializer(serializers.ModelSerializer):
    """Serializer for TrainerReview model."""

    class Meta:
        model = TrainerReview
        fields = [
            "id",
            "trainer",
            "user",
            "rating",
            "title",
            "text",
            "is_approved",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "is_approved", "created_at", "updated_at"]


class TrainerReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating TrainerReview."""

    class Meta:
        model = TrainerReview
        fields = [
            "trainer",
            "rating",
            "title",
            "text",
        ]

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        trainer = attrs.get("trainer")

        # User cannot review themselves
        if trainer == user:
            raise serializers.ValidationError(
                {"trainer": "You cannot review yourself."}
            )

        # Trainer must be an actual trainer
        if trainer and not trainer.is_trainer:
            raise serializers.ValidationError(
                {"trainer": "You can only review trainers."}
            )

        # Check if user already reviewed this trainer
        if TrainerReview.objects.filter(trainer=trainer, user=user).exists():
            raise serializers.ValidationError(
                {"trainer": "You have already reviewed this trainer."}
            )

        return attrs

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
