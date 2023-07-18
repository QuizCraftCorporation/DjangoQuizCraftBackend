"""
Module for asynchronously creating quizzes from files  .
"""
import datetime
from typing import Union

from app.celery import app
from app.settings import SEARCH_DB
from quiz.models import Quiz
from QuizGeneratorModel.quiz_craft_package.quiz_describer import QuizDescriber
from QuizGeneratorModel.quiz_craft_package.quiz_stream_generator import (
    QuizStreamGenerator,
)


@app.task(bind=True)
def create_quiz(
    self,
    file_names: list[str],
    pk: int,
    max_questions: Union[int, None] = None,
    description: Union[str, None] = None,
):
    """
    Create quiz from files.
    The function first creates a `QuizStreamGenerator` object and uses it to create a `NagimQuiz` object from the files.
    Then, it adds the questions from the `NagimQuiz` object to the quiz. If a description is provided, it sets the
    description of the `NagimQuiz` object and the quiz. Finally, it saves the quiz to the database and saves the
    `NagimQuiz` object to the vector database.

    The function returns the metadata of the generation process.

    Args:
        file_names: List of file names.
        pk: Quiz id.
        max_questions: Max questions.
        description: Quiz description.

    Returns:
        Metadata of generation process.
        """
    quiz = Quiz.objects.get(
        pk=pk
    )  # Getting quiz object from database for current quiz id
    quiz_gen = QuizStreamGenerator(debug=False)  # Quiz generator model
    meta = {"current": 0, "total": 0}  # Meta data of generation process
    ml_quiz = None  # The reference for the generated quiz
    try:
        for temp_quiz, i, n in quiz_gen.create_quiz_from_files(
            file_names, **{"max_questions": max_questions}
        ):
            meta = {
                "current": i,
                "total": n,
            }  # Meta data of generation process
            self.update_state(state="PROGRESS", meta=meta)
            ml_quiz = temp_quiz  # The reference for the generated quiz
    except Exception as e:
        # Removing temporary quiz from the database because of error in
        # creation process
        quiz.delete()
        self.update_state(
            state="FAILURE", meta=meta
        )  # Updating state to failure
        return e.__str__()  # Returning error message
    self.update_state(
        state="PREPARING DOCUMENTATION", meta=meta
    )  # Continuing with documentation preparing stage
    questions = [
        ml_quiz.get_question(i) for i in range(len(ml_quiz))
    ]  # Fetching questions from ml quiz model
    quiz.add_questions(questions)  # Adding questions to the quiz
    if description:
        ml_quiz.set_description(
            description
        )  # Setting description in vector database
    else:
        describer = QuizDescriber()  # Initializing quiz description generating
        ml_quiz = describer.generate_description(
            ml_quiz
        )  # Updating quiz with description
        quiz.description = (
            ml_quiz.description
        )  # Updating description for the quiz
    quiz.created_at = (
        datetime.datetime.now()
    )  # Setting creation time of the quiz
    quiz.ready = True  # Setting the quiz to ready state
    quiz.save()  # Saving quiz to database
    SEARCH_DB.save_quiz(
        quiz=ml_quiz, unique_id=str(quiz.id)
    )  # Saving quiz to vector database
    print(
        f"Quiz {pk} was created successfully"
    )  # Printing message for logging
    return meta
