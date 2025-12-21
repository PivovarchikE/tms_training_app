from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ReviewViewSet, TrainerReviewViewSet

router = DefaultRouter()
router.register(r"reviews", ReviewViewSet, basename="review")
router.register(r"trainer-reviews", TrainerReviewViewSet, basename="trainer-review")

urlpatterns = [
    path("", include(router.urls)),
]
