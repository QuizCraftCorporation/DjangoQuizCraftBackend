from celery import shared_task

from QuizGeneratorModel.quiz_craft_package.quiz_generator import QuizGenerator
from quiz.models import Quiz


@shared_task
def create_quiz(file_names, pk, max_questions):
    print(123)
    quiz = Quiz.objects.get(pk=pk)
    quiz_gen = QuizGenerator(debug=False)
    if max_questions:
        result = quiz_gen.create_questions_from_files(file_names,
                                                      max_questions=max_questions)
    else:
        result = quiz_gen.create_questions_from_files(file_names)
    quiz.add_questions(result)
    quiz.ready = True
    quiz.save()
    return f'Quiz {pk} was created successfully'