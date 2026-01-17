from rest_framework import serializers

from .models import ExerciseResult, WorkoutSession


class ExerciseResultSerializer(serializers.ModelSerializer):
    """Serializer for ExerciseResult model."""

    class Meta:
        model = ExerciseResult
        fields = [
            "id",
            "exercise",
            "exercise_name",
            "sets_completed",
            "reps",
            "weight",
            "duration_seconds",
            "distance_meters",
            "completed",
            "notes",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class WorkoutSessionSerializer(serializers.ModelSerializer):
    """Serializer for WorkoutSession model."""

    exercise_results = ExerciseResultSerializer(many=True, read_only=True)

    class Meta:
        model = WorkoutSession
        fields = [
            "id",
            "user",
            "plan",
            "title",
            "description",
            "scheduled_date",
            "started_at",
            "completed_at",
            "duration_minutes",
            "status",
            "notes",
            "calories_burned",
            "rating",
            "exercise_results",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["user", "created_at", "updated_at"]


class WorkoutSessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating WorkoutSession."""

    class Meta:
        model = WorkoutSession
        fields = [
            "plan",
            "title",
            "description",
            "scheduled_date",
            "notes",
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class WorkoutSessionUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating WorkoutSession."""

    class Meta:
        model = WorkoutSession
        fields = [
            "title",
            "description",
            "scheduled_date",
            "notes",
            "calories_burned",
            "rating",
        ]
