from django.urls import path
from quiz.views import QuizCreateView, QuizView, QuizAnswersView

urlpatterns = [
    path('create/', QuizCreateView.as_view(), name='create_quiz'),
    path('<int:id>/', QuizView.as_view(), name='get_quiz'),
    path('answers/<int:id>/', QuizAnswersView.as_view(), name='get_quiz_with_answers')
]
