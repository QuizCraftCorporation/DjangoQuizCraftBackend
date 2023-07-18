from django.urls import include, path
from rest_framework.routers import DefaultRouter

from quiz.views import QuizViewSet

router = DefaultRouter()
router.register("", QuizViewSet, basename="quiz")

urlpatterns = [
    path("", include(router.urls)),
]
