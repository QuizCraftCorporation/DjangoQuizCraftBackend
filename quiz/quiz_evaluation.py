from abc import ABC, abstractmethod


class QuestionEvaluator(ABC):
    """
    Abstract base class for question evaluators.

    Attributes:
        question : Question.
        answer : Question answer.
    """

    def __init__(self, question):
        """
        Initialize the question evaluator.

        Args:
            answer : Question answer.
        """
        self.question = question
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
        question : Question.
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


class MCQQuestionRationalEvaluator(QuestionEvaluator):
    """
    A question evaluator for multiple choice questions with binary answers.

    Attributes:
        question : Question.
        answer : Question answer.
    """

    def evaluate(self, user_answer):
        """
        Evaluate the user's answer.

        Args:
            user_answer (set[int]): The user's answer.

        Returns:
            float: The score for the user's answer.
        """
        options_length = len(self.question.options.all())
        answer_length = len(self.answer)
        correct_num = 0
        for answer in user_answer:
            if answer in self.answer:
                correct_num += 1
        encouragement = correct_num / answer_length if answer_length else 0
        penalty = (answer_length - correct_num) / \
                  (options_length - answer_length) \
            if options_length != answer_length else 0
        score = encouragement - penalty
        return score if score > 0 else 0


class TrueFalseQuestionEvaluator(QuestionEvaluator):
    """
    A question evaluator for true/false questions.

    Attributes:
        question : Question.
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
        question : Question.
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
        question : Question.
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
