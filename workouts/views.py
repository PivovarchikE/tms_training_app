from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import ExerciseResult, WorkoutSession
from .serializers import (
    ExerciseResultSerializer,
    WorkoutSessionCreateSerializer,
    WorkoutSessionSerializer,
    WorkoutSessionUpdateSerializer,
)


class IsOwner(permissions.BasePermission):
    """Only allow owners to access their objects."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class WorkoutSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for WorkoutSession model.

    Endpoints:
    - GET /workouts/ - list user's workouts
    - POST /workouts/ - create new workout
    - GET /workouts/{id}/ - retrieve workout
    - PUT/PATCH /workouts/{id}/ - update workout
    - DELETE /workouts/{id}/ - delete workout
    - POST /workouts/{id}/start/ - start workout
    - POST /workouts/{id}/complete/ - complete workout
    - POST /workouts/{id}/cancel/ - cancel workout
    - POST /workouts/{id}/skip/ - skip workout
    - GET /workouts/upcoming/ - list upcoming workouts
    - GET /workouts/history/ - list completed workouts
    - GET /workouts/stats/ - get workout statistics
    """

    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        queryset = WorkoutSession.objects.filter(user=user)

        # Filter by status if provided
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by date range
        date_from = self.request.query_params.get("date_from")
        date_to = self.request.query_params.get("date_to")
        if date_from:
            queryset = queryset.filter(scheduled_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(scheduled_date__lte=date_to)

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return WorkoutSessionCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return WorkoutSessionUpdateSerializer
        return WorkoutSessionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def start(self, request, pk=None):
        """Start a workout session."""
        workout = self.get_object()

        if workout.status != WorkoutSession.Status.SCHEDULED:
            return Response(
                {"error": "Can only start scheduled workouts."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        workout.start_workout()
        return Response(WorkoutSessionSerializer(workout).data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Complete a workout session."""
        workout = self.get_object()

        if workout.status != WorkoutSession.Status.IN_PROGRESS:
            return Response(
                {"error": "Can only complete in-progress workouts."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        workout.complete_workout()

        # Optionally update rating and calories from request
        rating = request.data.get("rating")
        calories = request.data.get("calories_burned")

        if rating:
            workout.rating = rating
        if calories:
            workout.calories_burned = calories
        if rating or calories:
            workout.save()

        return Response(WorkoutSessionSerializer(workout).data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a workout session."""
        workout = self.get_object()

        if workout.status in [
            WorkoutSession.Status.COMPLETED,
            WorkoutSession.Status.CANCELLED,
        ]:
            return Response(
                {"error": "Cannot cancel completed or already cancelled workouts."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        workout.cancel_workout()
        return Response(WorkoutSessionSerializer(workout).data)

    @action(detail=True, methods=["post"])
    def skip(self, request, pk=None):
        """Skip a workout session."""
        workout = self.get_object()

        if workout.status != WorkoutSession.Status.SCHEDULED:
            return Response(
                {"error": "Can only skip scheduled workouts."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        workout.skip_workout()
        return Response(WorkoutSessionSerializer(workout).data)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """List upcoming scheduled workouts."""
        queryset = (
            self.get_queryset()
            .filter(
                status=WorkoutSession.Status.SCHEDULED,
                scheduled_date__gte=timezone.now(),
            )
            .order_by("scheduled_date")
        )

        serializer = WorkoutSessionSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def history(self, request):
        """List completed workouts."""
        queryset = (
            self.get_queryset()
            .filter(
                status=WorkoutSession.Status.COMPLETED,
            )
            .order_by("-completed_at")
        )

        serializer = WorkoutSessionSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get workout statistics for current user."""
        queryset = self.get_queryset()

        total_workouts = queryset.count()
        completed_workouts = queryset.filter(
            status=WorkoutSession.Status.COMPLETED
        ).count()
        total_duration = sum(
            w.duration_minutes or 0
            for w in queryset.filter(status=WorkoutSession.Status.COMPLETED)
        )
        total_calories = sum(
            w.calories_burned or 0
            for w in queryset.filter(status=WorkoutSession.Status.COMPLETED)
        )

        # Calculate average rating
        rated_workouts = queryset.filter(rating__isnull=False)
        avg_rating = None
        if rated_workouts.exists():
            avg_rating = round(
                sum(w.rating for w in rated_workouts) / rated_workouts.count(), 2
            )

        return Response(
            {
                "total_workouts": total_workouts,
                "completed_workouts": completed_workouts,
                "completion_rate": (
                    round(completed_workouts / total_workouts * 100, 1)
                    if total_workouts > 0
                    else 0
                ),
                "total_duration_minutes": total_duration,
                "total_calories_burned": total_calories,
                "average_rating": avg_rating,
            }
        )

    @action(detail=True, methods=["post"], url_path="add-result")
    def add_result(self, request, pk=None):
        """Add exercise result to workout."""
        workout = self.get_object()
        serializer = ExerciseResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(session=workout)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExerciseResultViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ExerciseResult model.

    Endpoints:
    - GET /results/ - list exercise results
    - POST /results/ - create new result
    - GET /results/{id}/ - retrieve result
    - PUT/PATCH /results/{id}/ - update result
    - DELETE /results/{id}/ - delete result
    - POST /results/{id}/mark-complete/ - mark exercise as completed
    """

    serializer_class = ExerciseResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = ExerciseResult.objects.filter(session__user=user)

        # Filter by session if provided
        session_id = self.request.query_params.get("session")
        if session_id:
            queryset = queryset.filter(session_id=session_id)

        # Filter by completed status
        completed = self.request.query_params.get("completed")
        if completed is not None:
            queryset = queryset.filter(completed=completed.lower() == "true")

        return queryset

    @action(detail=True, methods=["post"], url_path="mark-complete")
    def mark_complete(self, request, pk=None):
        """Mark exercise result as completed."""
        result = self.get_object()
        result.completed = True
        result.save()
        return Response(ExerciseResultSerializer(result).data)
