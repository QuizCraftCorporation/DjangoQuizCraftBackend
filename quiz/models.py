"""
Module for quiz app database models
"""

import random
from abc import abstractmethod

from django.db import models
from django.utils.translation import gettext_lazy as _

from authorization.models import User
from .quiz_evaluation import (
    MCQQuestionBinaryEvaluator,
    TrueFalseQuestionEvaluator,
    OpenEndedQuestionEvaluator,
    InsertionQuestionEvaluator
)


class KeyWord(models.Model):
    """
    Key Word model.
    Used for adding new keywords to the quiz
    and group of quizzes.
    """
    name = models.CharField(_('key word'), primary_key=True, unique=True, max_length=30)

    class Meta:
        verbose_name = _("key word")
        verbose_name_plural = _("key words")


class Topic(models.Model):
    """
    Topic model.
    Used for in quizzes as quiz topic.
    """

    name = models.CharField(_("topic name"), max_length=42,
                            null=False, blank=False, primary_key=True)
    description = models.TextField(_("topic description"), blank=True)
    key_words = models.ManyToManyField(to=KeyWord)

    class Meta:
        verbose_name = _("topic")
        verbose_name_plural = _("topics")


class Material(models.Model):
    """
    Material model.
    Used for saving info about materials given by users.
    """
    name = models.CharField(_("material name"), max_length=60, null=False, blank=True)
    id = models.BigAutoField(verbose_name="material id", primary_key=True)
    file = models.FileField(upload_to="materials/")
    topic = models.ForeignKey(to=Topic, on_delete=models.PROTECT, verbose_name="topic", null=True)

    class Meta:
        verbose_name = _("material")
        verbose_name_plural = _("materails")


class Quiz(models.Model):
    """
    Quiz model used for saving info about quiz.
    Provides some features that can ve performed with quizzes.
    """
    name = models.TextField(blank=False, null=False)
    id = models.BigAutoField(verbose_name="quiz id", primary_key=True)
    sources = models.ManyToManyField(to=Material, verbose_name="sources")
    topic = models.ForeignKey(to=Topic, on_delete=models.PROTECT, verbose_name="topic", null=True)
    passed_users = models.ManyToManyField(User, through="Take")
    creator = models.ForeignKey(
        to=User, on_delete=models.PROTECT,
        verbose_name="creator id", related_name="quizzes",
        null=True
    )
    description = models.TextField(blank=False, max_length=400)
    private = models.BooleanField(default=False)
    ready = models.BooleanField(default=False)

    REQUIRED_FIELDS = ["name"]

    def add_questions(self, model_questions):
        mcqs = []
        for question in model_questions:
            q = Question.objects.create(text=question[0], type_id=1, quiz=self)
            correct_options = set(question[2])
            options = []
            mcq = MCQQuestion.objects.create(question=q)
            for i in range(len(question[1])):
                correct = i in correct_options
                options.append(MCQOption(text=question[1][i], correct=correct, question=mcq))
            random.shuffle(options)
            for option in options:
                option.save()
                mcq.options.add(option)
            mcq.save()

    class Meta:
        verbose_name = _("quiz")
        verbose_name_plural = _("quizzes")


class QuizGroup(models.Model):
    """
    Quiz Group model.
    Contains info about quiz groups.
    """
    name = models.CharField(_("group name"), max_length=42, null=False, blank=False)
    id = models.BigAutoField(_("group id"), primary_key=True)
    quizzes = models.ManyToManyField(Quiz)

    class Meta:
        verbose_name = _("quiz group")
        verbose_name_plural = _("quiz groups")


class Question(models.Model):
    """
    Question model.
    Contains basic information about questions and their type id.
    """
    MCQ = 1
    TRUE_FALSE = 2
    INSERTION = 3
    OPEN_ENDED = 4

    QUESTION_TYPE = (
        (MCQ, _("MCQ Question")),
        (TRUE_FALSE, _("True/False Question")),
        (INSERTION, _("Insertion Question")),
        (OPEN_ENDED, _("Open Ended Question")),
    )

    id = models.BigAutoField(verbose_name="question id", primary_key=True)
    text = models.TextField(_("question text"))
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, null=True)
    type_id = models.PositiveSmallIntegerField(
        default=1,
        choices=QUESTION_TYPE
    )

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")

    def get_question_with_type(self):
        if self.type_id == 1:
            return self.mcq_question
        elif self.type_id == 2:
            return self.true_false_question
        elif self.type_id == 3:
            return self.insertion_question
        elif self.type_id == 4:
            return self.open_ended_question
        else:
            return self


class AbstractQuestion(models.Model):
    """
    Abstract base class for all other question models.

    Defines two abstract methods: `get_answer()` and `get_evaluator()`.

    The `get_answer()` method should return the answer for the current question,
    and the `get_evaluator()` method should return a class that can be used to
    evaluate the answer to the current question.

    The abstract question model is used to decouple the question models from
    the question evaluators. This makes it easier to add new question types,
    as the new question types only need to implement the `get_answer()` and
    `get_evaluator()` methods.
    """

    class Meta:
        abstract = True

    @abstractmethod
    def get_answer(self):
        """
        Get answer for current question.
        """

    @staticmethod
    @abstractmethod
    def get_evaluator():
        """
        Get evaluator for current question.

        Returns:
            type[QuestionEvaluator]: Evaluator
        """


class MCQOption(models.Model):
    text = models.CharField(_("option text"))
    id = models.AutoField(_("option id"), primary_key=True)
    question = models.ForeignKey(
        "MCQQuestion", on_delete=models.CASCADE, verbose_name="question", null=True,
        related_name="options"
    )
    correct = models.BooleanField(_("correct"), default=False)

    class Meta:
        verbose_name = _("Multiple Choice Question option")
        verbose_name_plural = _("Multiple Choice Question options")


class MCQQuestion(AbstractQuestion):
    """
    Class represents a multiple choice question.

    Inherits from the `AbstractQuestion` class and implements the
    `get_answer()` and `get_evaluator()` methods.

    The `get_answer()` method returns a set of the IDs of the correct options
    for the question.

    The `get_evaluator()` method returns a class that can evaluate a user's
    answer to the question by checking whether it is one of the correct options.
    """

    class Meta:
        verbose_name = _("Multiple Choice Question")
        verbose_name_plural = _("Multiple Choice Questions")

    question = models.OneToOneField(Question, verbose_name="question id", on_delete=models.CASCADE,
                                    primary_key=True, default=0, related_name="mcq_question")

    def get_answer(self):
        """
        Get set of answer ids for MCQ question.

        Returns:
            set[int]: Set of answer ids.
        """
        question_answers = {
            option.id for option
            in self.options.filter(correct__exact=True)
        }
        return question_answers

    @staticmethod
    def get_evaluator():
        """
        Get specific evaluator for MCQ question.

        Returns:
            type[MCQQuestionBinaryEvaluator]: MCQ evaluator
        """

        return MCQQuestionBinaryEvaluator


class TrueFalseQuestion(AbstractQuestion):
    """
    Class represents a true/false question.

    Inherits from the `AbstractQuestion` class and implements the
    `get_answer()` and `get_evaluator()` methods.

    The `get_answer()` method returns a boolean value indicating whether the
    correct answer is true or false.

    The `get_evaluator()` method returns a class that can evaluate a user's
    answer to the question by checking whether it is the same as the correct answer.
    """

    class Meta:
        verbose_name = _("true/false question")
        verbose_name_plural = _("true/false questions")

    question = models.OneToOneField(Question, verbose_name="question id", on_delete=models.CASCADE,
                                    primary_key=True, default=0, related_name="true_false_question")
    answer = models.BooleanField(verbose_name="answer flag")

    def get_answer(self):
        """
        Get answer flag for current true/false question.

        Returns:
            bool: Correct answer flag.
        """
        return self.answer

    @staticmethod
    def get_evaluator():
        """
        Get specific evaluator for True/False question.

        Returns:
            type[TrueFalseQuestionEvaluator]: True/False evaluator
        """

        return TrueFalseQuestionEvaluator


class OpenEndedQuestion(AbstractQuestion):
    """
    Class represents an open ended question.

    Inherits from the `AbstractQuestion` class and implements the
    `get_answer()` and `get_evaluator()` methods.

    The `get_answer()` method returns the text of the answer for the question.

    The `get_evaluator()` method returns a class that can evaluate a user's
    answer to the question by comparing it to the text of the correct answer.
    """

    question = models.OneToOneField(Question, verbose_name="question id", on_delete=models.CASCADE,
                                    primary_key=True, default=0, related_name="open_ended_question")
    answer = models.TextField(verbose_name="open answer")

    class Meta:
        verbose_name = _("open ended question")
        verbose_name_plural = _("opend ended questions")

    def get_answer(self):
        """
        Get answer text for current question.

        Returns:
            str: Answer text.
        """
        return self.answer

    @staticmethod
    def get_evaluator():
        """
        Get specific evaluator for Open Ended question.

        Returns:
            type[OpenEndedQuestionEvaluator]: True/False evaluator
        """

        return OpenEndedQuestionEvaluator


class InsertionPosition(models.Model):
    """
    Model representing a position in an insertion question.

    Attributes:
        question (models.ForeignKey): The insertion question this position is
            associated with.
        position (PositiveIntegerField): The position of the answer in the
            insertion question.
    """

    class Meta:
        unique_together = (('question', 'position'),)

    def __str__(self):
        return f"InsertionPosition(question={self.question}, position={self.position})"

    question = models.ForeignKey(to="InsertionQuestion", verbose_name="question id", null=False,
                                 on_delete=models.CASCADE)
    position = models.PositiveIntegerField(verbose_name="position offset", null=False)


class InsertionQuestion(AbstractQuestion):
    """
    Model representing an insertion question.

    Attributes:
        question (models.OneToOneField): The base question model for this
            insertion question.
        insertion_text (TextField): The text that the user must insert into the
            insertion question.
    """

    def __str__(self):
        return f"InsertionQuestion(question={self.question}, insertion_text={self.insertion_text})"

    question = models.OneToOneField(Question, verbose_name="question id", on_delete=models.CASCADE,
                                    primary_key=True, default=0, related_name="insertion_question")
    insertion_text = models.TextField(verbose_name="text for insertion")

    def get_answer(self):
        """
        Get answer text for current question.

        Returns:
            list[str]: List of answers in correct order.
        """
        answers = [
            insertion_answer.answer for insertion_answer
            in map(
                lambda insertion_answer: insertion_answer.answer,
                sorted(
                    self.insertion_answers.all(),
                    key=lambda x: x.position
                )
            )
        ]
        return answers

    @staticmethod
    def get_evaluator():
        """
        Get specific evaluator for Open Ended question.

        Returns:
            type[OpenEndedQuestionEvaluator]: True/False evaluator
        """

        return InsertionQuestionEvaluator


class InsertionAnswer(models.Model):
    """
    Model representing an answer to an insertion question.

    Attributes:
        question (models.ForeignKey): The insertion question this answer is
            associated with.
        answer (TextField): The answer text.
        position (PositiveIntegerField): The position of the answer in the
            insertion question.
    """

    def __str__(self):
        return f"InsertionAnswer(question={self.question}, answer={self.answer}, " \
               f"position={self.position})"

    question = models.ForeignKey(to=InsertionQuestion, verbose_name="question id", null=False,
                                 on_delete=models.CASCADE, related_name="insertion_answers")
    answer = models.TextField(_("text to insert"))
    position = models.PositiveIntegerField(verbose_name="position offset", null=False)


class Take(models.Model):
    """
    Model representing a user's take on a quiz.

    Attributes:
        quiz (models.ForeignKey): The quiz that the user took.
        user (models.ForeignKey): The user who took the quiz.
        points (FloatField): The number of points the user scored on the quiz.
        passage_date (DateField): The date the user took the quiz.
    """

    def __str__(self):
        return f"Take(quiz={self.quiz}, user={self.user}, points={self.points}, " \
               f"passage_date={self.passage_date})"

    quiz = models.ForeignKey(to=Quiz, on_delete=models.PROTECT, verbose_name="quiz id")
    user = models.ForeignKey(to=User, on_delete=models.PROTECT, verbose_name="user id")
    points = models.FloatField(_("points"))
    passage_date = models.DateField(_("passage date"), auto_now_add=True, null=False)
    id = models.BigAutoField(_("take id"), primary_key=True, auto_created=True, db_index=True)

    class Meta:
        verbose_name = _("take")
        verbose_name_plural = _("takes")
