from abc import ABC, abstractmethod


class BaseQuestionEvaluator(ABC):

    @staticmethod
    @abstractmethod
    def evaluate(question, user_answer):
        pass


class MCQQuestionBinaryEvaluator(BaseQuestionEvaluator):

    @staticmethod
    def evaluate(question, user_answer):
        if question.answer.id == user_answer:
            return 1
        return 0


