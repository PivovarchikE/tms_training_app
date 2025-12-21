from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ExerciseViewSet, TrainingPlanViewSet, UserPlanAssignmentViewSet

router = DefaultRouter()
router.register(r"plans", TrainingPlanViewSet, basename="training-plan")
router.register(r"exercises", ExerciseViewSet, basename="exercise")
router.register(r"assignments", UserPlanAssignmentViewSet, basename="assignment")

urlpatterns = [
    path("", include(router.urls)),
]
