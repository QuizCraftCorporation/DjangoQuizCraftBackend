from celery import shared_task

from QuizGeneratorModel.quiz_craft_package.quiz_generator import QuizGenerator


@shared_task
def create_quiz(materials, quiz, max_questions):
    quiz_gen = QuizGenerator(debug=False)
    if max_questions:
        result = quiz_gen.create_questions_from_files([str(material.file.file) for material in materials],
                                                      max_questions=max_questions)
    else:
        result = quiz_gen.create_questions_from_files([str(material.file.file) for material in materials])
    quiz.add_questions(result)
    quiz.ready = True
    quiz.save()