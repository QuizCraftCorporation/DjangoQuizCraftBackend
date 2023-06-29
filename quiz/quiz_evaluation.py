from abc import ABC, abstractmethod


class QuestionEvaluator(ABC):
    """
    Abstract base class for question evaluators.

    Attributes:
        answer : Correct answer on question.
    """

    def __init__(self, answer):
        """
        Initialize the question evaluator.

        Args:
            answer : Correct answer on question.
        """
        self.answer = answer

    @abstractmethod
    def evaluate(self, user_answer):
        """
        Evaluate the user's answer.

        Args:
            user_answer (set[int]): The user's answer.

        Returns:
            int: The score for the user's answer.
        """


class MCQQuestionBinaryEvaluator(QuestionEvaluator):
    """
    A question evaluator for multiple choice questions with binary answers.

    Attributes:
        question (Question): The question to be evaluated.
    """

    def evaluate(self, user_answer):
        """
        Evaluate the user's answer.

        Args:
            user_answer (str): The user's answer.

        Returns:
            int: The score for the user's answer.
        """
        if all(answer in self.answer for answer in user_answer):
            return 1
        return 0
