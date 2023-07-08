from celery import shared_task

from QuizGeneratorModel.quiz_craft_package.containers.nagim_quiz import NagimQuiz
from QuizGeneratorModel.quiz_craft_package.quiz_generator import QuizGenerator
from app.settings import SEARCH_DB
from quiz.models import Quiz


@shared_task
def create_quiz(file_names: list[str], pk: int, max_questions: int | None = None, description: str | None = None):
    quiz = Quiz.objects.get(pk=pk)
    quiz_gen = QuizGenerator(debug=False)
    if max_questions:
        ml_quiz: NagimQuiz = quiz_gen.create_quiz_from_files(file_names,
                                                             max_questions=max_questions)
    else:
        ml_quiz: NagimQuiz = quiz_gen.create_quiz_from_files(file_names)
    questions = [ml_quiz.get_question(i) for i in range(len(ml_quiz))]
    quiz.add_questions(questions)
    quiz.ready = True
    if description:
        ml_quiz.set_description(description)
    quiz.description = ml_quiz.description
    quiz.save()
    SEARCH_DB.save_quiz(quiz=ml_quiz, unique_id=str(quiz.id))
    return f'Quiz {pk} was created successfully'
