from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Review, TrainerReview
from .serializers import (
    ReviewCreateSerializer,
    ReviewSerializer,
    TrainerReviewCreateSerializer,
    TrainerReviewSerializer,
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Allow owners to edit, others can only read."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Review model (plan reviews).

    Endpoints:
    - GET /reviews/ - list all approved reviews
    - POST /reviews/ - create new review
    - GET /reviews/{id}/ - retrieve review
    - PUT/PATCH /reviews/{id}/ - update review (owner only)
    - DELETE /reviews/{id}/ - delete review (owner only)
    - GET /reviews/my/ - list current user's reviews
    - GET /reviews/plan/{plan_id}/ - list reviews for a plan
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Review.objects.filter(is_approved=True)

        # Filter by plan if provided
        plan_id = self.request.query_params.get("plan")
        if plan_id:
            queryset = queryset.filter(plan_id=plan_id)

        # Filter by rating if provided
        min_rating = self.request.query_params.get("min_rating")
        if min_rating:
            queryset = queryset.filter(rating__gte=int(min_rating))

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return ReviewCreateSerializer
        return ReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="my")
    def my_reviews(self, request):
        """List current user's reviews."""
        queryset = Review.objects.filter(user=request.user)
        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="plan/(?P<plan_id>[^/.]+)")
    def plan_reviews(self, request, plan_id=None):
        """List reviews for a specific plan."""
        queryset = Review.objects.filter(plan_id=plan_id, is_approved=True)
        serializer = ReviewSerializer(queryset, many=True)
        return Response(serializer.data)


class TrainerReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TrainerReview model.

    Endpoints:
    - GET /trainer-reviews/ - list all approved trainer reviews
    - POST /trainer-reviews/ - create new review
    - GET /trainer-reviews/{id}/ - retrieve review
    - PUT/PATCH /trainer-reviews/{id}/ - update review (owner only)
    - DELETE /trainer-reviews/{id}/ - delete review (owner only)
    - GET /trainer-reviews/my/ - list current user's reviews
    - GET /trainer-reviews/trainer/{trainer_id}/ - list reviews for a trainer
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = TrainerReview.objects.filter(is_approved=True)

        # Filter by trainer if provided
        trainer_id = self.request.query_params.get("trainer")
        if trainer_id:
            queryset = queryset.filter(trainer_id=trainer_id)

        # Filter by rating if provided
        min_rating = self.request.query_params.get("min_rating")
        if min_rating:
            queryset = queryset.filter(rating__gte=int(min_rating))

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return TrainerReviewCreateSerializer
        return TrainerReviewSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], url_path="my")
    def my_reviews(self, request):
        """List current user's trainer reviews."""
        queryset = TrainerReview.objects.filter(user=request.user)
        serializer = TrainerReviewSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="trainer/(?P<trainer_id>[^/.]+)")
    def trainer_reviews(self, request, trainer_id=None):
        """List reviews for a specific trainer."""
        queryset = TrainerReview.objects.filter(trainer_id=trainer_id, is_approved=True)
        serializer = TrainerReviewSerializer(queryset, many=True)
        return Response(serializer.data)
