from django.urls import path

from quiz.views import QuizAnswersView, QuizCreateView, QuizView, QuizEvaluate, QuizViewMe

urlpatterns = [
    path('create/', QuizCreateView.as_view(), name='create_quiz'),
    path('list/', QuizViewMe.as_view(), name='list_quizzes'),
    path('<int:id>/', QuizView.as_view(), name='get_quiz'),
    path('answers/<int:id>/', QuizAnswersView.as_view(), name='get_quiz_with_answers'),
    path('attempt/', QuizEvaluate.as_view(), name='attempt_quiz'),
]
