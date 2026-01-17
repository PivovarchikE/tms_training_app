from django.db.models import Q
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Exercise, TrainingPlan, UserPlanAssignment
from .serializers import (
    ExerciseCreateSerializer,
    ExerciseSerializer,
    TrainingPlanCreateSerializer,
    TrainingPlanListSerializer,
    TrainingPlanSerializer,
    UserPlanAssignmentCreateSerializer,
    UserPlanAssignmentSerializer,
)


class IsTrainerOrReadOnly(permissions.BasePermission):
    """Allow trainers to edit, others can only read."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_trainer


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow owners to edit their objects."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.trainer == request.user


# @extend_schema_view(
#     list=extend_schema(summary="List exercises", description="List all exercises"),
#     update=extend_schema(summary='Update exercise', description="Update some exercises"),
#     partial_update=extend_schema(summary="Partially update exercise", description="Partially update some exercise"),
#     create=extend_schema(summary="Create new exercise", description="Create a new exercise description"),
#     retrieve=extend_schema(summary='Retrieve exercise', description="Retrieve some exercise"),
#     destroy=extend_schema(summary='Delete exercise', description="Delete some exercise"),
#     my_plans=extend_schema(summary='List training plans', description="List training plans description"),
#     add_exercise=extend_schema(summary='Add exercise', description="Add exercise"),
# )
class TrainingPlanViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TrainingPlan model.

    Endpoints:
    - GET /plans/ - list public plans (or all for trainers)
    - POST /plans/ - create new plan (trainers only)
    - GET /plans/{id}/ - retrieve plan
    - PUT/PATCH /plans/{id}/ - update plan (owner only)
    - DELETE /plans/{id}/ - delete plan (owner only)
    - GET /plans/my/ - list trainer's own plans
    """

    permission_classes = [IsTrainerOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user

        if self.action == "my_plans":
            return TrainingPlan.objects.filter(trainer=user)

        # Show public plans to everyone, private plans only to owners
        if user.is_authenticated and user.is_trainer:
            return TrainingPlan.objects.filter(Q(is_public=True) | Q(trainer=user))
        return TrainingPlan.objects.filter(is_public=True)

    def get_serializer_class(self):
        if self.action == "create":
            return TrainingPlanCreateSerializer
        elif self.action == "list":
            return TrainingPlanListSerializer
        return TrainingPlanSerializer

    def perform_create(self, serializer):
        serializer.save(trainer=self.request.user)

    @extend_schema(summary="Delete exercise", description="Delete some exercise")
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["get"], url_path="my")
    def my_plans(self, request):
        """List trainer's own plans."""
        queryset = self.get_queryset()
        serializer = TrainingPlanListSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], url_path="add-exercise")
    def add_exercise(self, request, pk=None):
        """Add exercise to a training plan."""
        plan = self.get_object()
        serializer = ExerciseCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(plan=plan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ExerciseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Exercise model.

    Endpoints:
    - GET /exercises/ - list exercises
    - POST /exercises/ - create new exercise (trainers only)
    - GET /exercises/{id}/ - retrieve exercise
    - PUT/PATCH /exercises/{id}/ - update exercise (plan owner only)
    - DELETE /exercises/{id}/ - delete exercise (plan owner only)
    """

    queryset = Exercise.objects.all()
    permission_classes = [IsTrainerOrReadOnly]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ExerciseCreateSerializer
        return ExerciseSerializer

    def get_queryset(self):
        queryset = Exercise.objects.all()

        # Filter by plan if provided
        plan_id = self.request.query_params.get("plan")
        if plan_id:
            queryset = queryset.filter(plan_id=plan_id)

        # Filter by muscle group if provided
        muscle_group = self.request.query_params.get("muscle_group")
        if muscle_group:
            queryset = queryset.filter(muscle_group=muscle_group)

        return queryset


class UserPlanAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserPlanAssignment model.

    Endpoints:
    - GET /assignments/ - list assignments
    - POST /assignments/ - create assignment (trainers only)
    - GET /assignments/{id}/ - retrieve assignment
    - PUT/PATCH /assignments/{id}/ - update assignment
    - DELETE /assignments/{id}/ - delete assignment
    - GET /assignments/my/ - list current user's assigned plans
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if self.action == "my_assignments":
            return UserPlanAssignment.objects.filter(user=user)

        # Trainers can see all assignments they made
        if user.is_trainer:
            return UserPlanAssignment.objects.filter(Q(assigned_by=user) | Q(user=user))

        # Regular users can only see their own assignments
        return UserPlanAssignment.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == "create":
            return UserPlanAssignmentCreateSerializer
        return UserPlanAssignmentSerializer

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)

    @action(detail=False, methods=["get"], url_path="my")
    def my_assignments(self, request):
        """List current user's assigned plans."""
        queryset = self.get_queryset()
        serializer = UserPlanAssignmentSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        """Mark assignment as completed."""
        assignment = self.get_object()
        assignment.status = UserPlanAssignment.Status.COMPLETED
        assignment.save()
        return Response(UserPlanAssignmentSerializer(assignment).data)

    @action(detail=True, methods=["post"])
    def pause(self, request, pk=None):
        """Pause assignment."""
        assignment = self.get_object()
        assignment.status = UserPlanAssignment.Status.PAUSED
        assignment.save()
        return Response(UserPlanAssignmentSerializer(assignment).data)

    @action(detail=True, methods=["post"])
    def resume(self, request, pk=None):
        """Resume paused assignment."""
        assignment = self.get_object()
        assignment.status = UserPlanAssignment.Status.ACTIVE
        assignment.save()
        return Response(UserPlanAssignmentSerializer(assignment).data)
