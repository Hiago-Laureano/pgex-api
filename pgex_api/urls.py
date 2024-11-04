from django.urls import path, include
from rest_framework import routers
from .views import SurveyViewSet

router = routers.SimpleRouter()
router.register("", SurveyViewSet)

urlpatterns = [
    path("v1/surveys/", include(router.urls))
]
