from abc import ABC, abstractmethod

from quiz.models import AbstractQuestion


class QuestionEvaluator(ABC):
    """
    Abstract base class for question evaluators.

    Attributes:
        answer : Question answer.
    """

    def __init__(self, question):
        """
        Initialize the question evaluator.

        Args:
            AbstractQuestion : Question instance.
        """
        self.answer = question.get_answer()

    @abstractmethod
    def evaluate(self, user_answer):
        """
        Evaluate the user's answer.

        Args:
            user_answer: The user's answer.

        Returns:
            int: The score for the user's answer.
        """


class MCQQuestionBinaryEvaluator(QuestionEvaluator):
    """
    A question evaluator for multiple choice questions with binary answers.

    Attributes:
        answer : Question answer.
    """

    def evaluate(self, user_answer):
        """
        Evaluate the user's answer.

        Args:
            user_answer (set[int]): The user's answer.

        Returns:
            int: The score for the user's answer.
        """
        return int(self.answer == user_answer)


class TrueFalseQuestionEvaluator(QuestionEvaluator):
    """
    A question evaluator for true/false questions.

    Attributes:
        answer : Question answer.
    """

    def evaluate(self, user_answer):
        """
        Evaluate the user's answer.

        Args:
            user_answer (bool): The user's answer.

        Returns:
            int: The score for the user's answer.
        """
        return int(self.answer == user_answer)


class OpenEndedQuestionEvaluator(QuestionEvaluator):
    """
    A question evaluator for open-ended questions.

    Attributes:
        answer : Question answer.
    """

    def evaluate(self, user_answer):
        """
        Evaluate the user's answer.

        Args:
            user_answer (str): The user's answer.

        Returns:
            int: The score for the user's answer.
        """
        return int(self.answer == user_answer)
