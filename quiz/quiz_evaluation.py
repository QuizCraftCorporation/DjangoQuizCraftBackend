"""
Module for question evaluation.

This module provides question evaluators for different types of questions.

The question evaluators are used to evaluate the user's answers to the questions
and return the score for the user's answer.
"""

from abc import ABC, abstractmethod


class QuestionEvaluator(ABC):
    """
    Abstract base class for question evaluators.

    Attributes:
        answer : Question answer.
    """

    def __init__(self, answer):
        """
        Initialize the question evaluator.

        Args:
            answer : Question answer.
        """
        self.answer = answer

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
        return int(self.answer == set(user_answer))


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


class InsertionQuestionEvaluator(QuestionEvaluator):
    """
    A question evaluator for insertion questions.

    Attributes:
        answer : Question answer.
    """

    def evaluate(self, user_answer):
        """
        Evaluate the user's answer.

        Args:
            user_answer (list[str]): The user's answer.

        Returns:
            int: The score for the user's answer.
        """

        return int(len(self.answer) == len(user_answer) and
                   all(self.answer == answer for answer in user_answer))
