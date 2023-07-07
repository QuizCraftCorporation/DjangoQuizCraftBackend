from celery import shared_task

from QuizGeneratorModel.quiz_craft_package.quiz_generator import QuizGenerator
from app.settings import SEARCH_DB
from quiz.models import Quiz


@shared_task
def create_quiz(file_names, pk, max_questions, description):
    print(123)
    quiz = Quiz.objects.get(pk=pk)
    quiz_gen = QuizGenerator(debug=False)
    if max_questions:
        result = quiz_gen.create_quiz_from_files(file_names,
                                                 max_questions=max_questions)
    else:
        result = quiz_gen.create_quiz_from_files(file_names)
    questions = [result.get_question(i) for i in range(len(result))]
    quiz.add_questions(questions)
    quiz.ready = True
    quiz.save()
    result.set_description(description)
    SEARCH_DB.save_quiz(quiz=result, unique_id=str(quiz.id))
    return f'Quiz {pk} was created successfully'
