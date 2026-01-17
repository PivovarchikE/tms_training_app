from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ExerciseResultViewSet, WorkoutSessionViewSet

router = DefaultRouter()
router.register(r"workouts", WorkoutSessionViewSet, basename="workout")
router.register(r"results", ExerciseResultViewSet, basename="exercise-result")

urlpatterns = [
    path("", include(router.urls)),
]
