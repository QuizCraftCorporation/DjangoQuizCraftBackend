from django.urls import path, include
from rest_framework.routers import DefaultRouter

from quiz.views import QuizViewSet

router = DefaultRouter()
router.register('', QuizViewSet, basename='quiz')

urlpatterns = [
    path('', include(router.urls)),
]
