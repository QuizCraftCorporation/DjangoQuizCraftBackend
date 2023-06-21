from django.urls import path
from quiz.views import QuizCreateView, QuizView, GetIndex

urlpatterns = [
    path('create/', QuizCreateView.as_view(), name='create_quiz'),
    path('<int:id>/', QuizView.as_view(), name='get_quiz')
]
