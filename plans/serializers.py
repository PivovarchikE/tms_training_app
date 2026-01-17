from rest_framework import serializers

from .models import Exercise, TrainingPlan, UserPlanAssignment


class ExerciseSerializer(serializers.ModelSerializer):
    """Serializer for Exercise model."""

    is_time_based = serializers.ReadOnlyField()

    class Meta:
        model = Exercise
        fields = [
            "id",
            "title",
            "description",
            "muscle_group",
            "order",
            "sets",
            "reps",
            "duration_seconds",
            "rest_seconds",
            "target_weight",
            "video_url",
            "image_url",
            "is_time_based",
        ]


class ExerciseCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Exercise."""

    class Meta:
        model = Exercise
        fields = [
            "title",
            "description",
            "muscle_group",
            "order",
            "sets",
            "reps",
            "duration_seconds",
            "rest_seconds",
            "target_weight",
            "video_url",
            "image_url",
        ]


class TrainingPlanSerializer(serializers.ModelSerializer):
    """Serializer for TrainingPlan model."""

    exercises = ExerciseSerializer(many=True, read_only=True)
    total_exercises = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = TrainingPlan
        fields = [
            "id",
            "trainer",
            "title",
            "description",
            "is_public",
            "difficulty",
            "category",
            "duration_weeks",
            "sessions_per_week",
            "exercises",
            "total_exercises",
            "average_rating",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["trainer", "created_at", "updated_at"]


class TrainingPlanCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating TrainingPlan."""

    class Meta:
        model = TrainingPlan
        fields = [
            "title",
            "description",
            "is_public",
            "difficulty",
            "category",
            "duration_weeks",
            "sessions_per_week",
        ]

    def create(self, validated_data):
        validated_data["trainer"] = self.context["request"].user
        return super().create(validated_data)


class TrainingPlanListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing TrainingPlans."""

    total_exercises = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = TrainingPlan
        fields = [
            "id",
            "trainer",
            "title",
            "is_public",
            "difficulty",
            "category",
            "duration_weeks",
            "sessions_per_week",
            "total_exercises",
            "average_rating",
            "created_at",
        ]


class UserPlanAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for UserPlanAssignment model."""

    plan = TrainingPlanListSerializer(read_only=True)

    class Meta:
        model = UserPlanAssignment
        fields = [
            "id",
            "user",
            "plan",
            "assigned_by",
            "status",
            "start_date",
            "end_date",
            "notes",
            "created_at",
        ]
        read_only_fields = ["assigned_by", "created_at"]


class UserPlanAssignmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating UserPlanAssignment."""

    class Meta:
        model = UserPlanAssignment
        fields = [
            "user",
            "plan",
            "start_date",
            "end_date",
            "notes",
        ]

    def create(self, validated_data):
        validated_data["assigned_by"] = self.context["request"].user
        return super().create(validated_data)
