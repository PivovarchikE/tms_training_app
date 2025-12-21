"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


# from rest_framework.routers import DefaultRouter

# from plans.views import TrainingPlanViewSet
# from users.views import UserViewSet
# from workouts.views import WorkoutSessionViewSet

# router = DefaultRouter()
# router.register("workouts", WorkoutSessionViewSet, basename="workouts")
# router.register("plans", TrainingPlanViewSet, basename="plans")
# router.register("users", UserViewSet, basename="users")

urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view()),
    path("admin/", admin.site.urls),
    path("api/", include("users.urls")),
    path("api/", include("workouts.urls")),
    path("api/", include("plans.urls")),
    path("api/", include("notifications.urls")),
    path("api/", include("reviews.urls")),
]
