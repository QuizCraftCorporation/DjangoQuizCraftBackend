from django.db import models
from django.utils.translation import gettext_lazy as _

from authorization.models import User


class KeyWord(models.Model):
    name = models.CharField(_('key word'), primary_key=True, unique=True, max_length=30)

    class Meta:
        verbose_name = _("key word")
        verbose_name_plural = _("key words")


class Topic(models.Model):
    name = models.CharField(_("topic name"), max_length=42, null=False, blank=False, primary_key=True)
    description = models.TextField(_("topic description"), blank=True)
    key_words = models.ManyToManyField(to=KeyWord)

    class Meta:
        verbose_name = _("topic")
        verbose_name_plural = _("topics")


class Material(models.Model):
    name = models.CharField(_("material name"), max_length=60, null=False, blank=False)
    id = models.BigAutoField(verbose_name="material id", primary_key=True)
    file_name = models.FileField(upload_to="materials/")
    topic = models.ForeignKey(to=Topic, on_delete=models.PROTECT, verbose_name="topic")

    class Meta:
        verbose_name = _("material")
        verbose_name_plural = _("materails")


class Quiz(models.Model):
    name = models.TextField(blank=False, null=False)
    id = models.BigAutoField(verbose_name="quiz id", primary_key=True)
    source_id = models.ForeignKey(to=Material, on_delete=models.CASCADE, verbose_name="source id")
    topic = models.ForeignKey(to=Topic, on_delete=models.PROTECT, verbose_name="topic")
    users = models.ManyToManyField(User)

    class Meta:
        verbose_name = _("quiz")
        verbose_name_plural = _("quizzes")


class QuizGroup(models.Model):
    name = models.CharField(_("group name"), max_length=42, null=False, blank=False)
    id = models.BigAutoField(_("group id"), primary_key=True)
    quizzes = models.ManyToManyField(Quiz)

    class Meta:
        verbose_name = _("quiz group")
        verbose_name_plural = _("quiz groups")


class Question(models.Model):
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
    type_id = models.PositiveSmallIntegerField(
        default=1,
        choices=QUESTION_TYPE
    )

    class Meta:
        verbose_name = _("question")
        verbose_name_plural = _("questions")


class MCQOption(models.Model):
    text = models.CharField(_("option text"))
    id = models.AutoField(_("option id"), primary_key=True)

    class Meta:
        verbose_name = _("Multiple Choice Question option")
        verbose_name_plural = _("Multiple Choice Question options")


class MCQQuestion(models.Model):
    id = models.BigAutoField(verbose_name="question id", primary_key=True)
    answer = models.IntegerField(verbose_name="answer id")
    options = models.ForeignKey(MCQOption, on_delete=models.CASCADE, verbose_name="options")

    class Meta:
        verbose_name = _("Multiple Choice Question")
        verbose_name_plural = _("Multiple Choice Questions")


class TrueFalseQuestion(models.Model):
    id = models.BigAutoField(verbose_name="question id", primary_key=True)
    answer = models.BooleanField(verbose_name="answer flag")

    class Meta:
        verbose_name = _("true/false question")
        verbose_name_plural = _("true/false questions")


class OpenEndedQuestion(models.Model):
    id = models.BigAutoField(verbose_name="question id", primary_key=True)
    answer = models.TextField(verbose_name="open answer")

    class Meta:
        verbose_name = _("open ended question")
        verbose_name_plural = _("opend ended questions")


class InsertionPosition(models.Model):
    question = models.ForeignKey(to="InsertionQuestion", verbose_name="question id", null=False,
                                 on_delete=models.CASCADE)
    position = models.PositiveIntegerField(verbose_name="position offset", null=False)

    class Meta:
        unique_together = (('question', 'position'),)


class InsertionQuestion(models.Model):
    id = models.BigAutoField(verbose_name="question id", primary_key=True)
    insertion_text = models.TextField(verbose_name="text for insertion")


class InsertionAnswer(models.Model):
    question = models.ForeignKey(to=InsertionQuestion, verbose_name="question id", null=False,
                                 on_delete=models.CASCADE)
    answer = models.TextField(_("text to insert"))
    position = models.PositiveIntegerField(verbose_name="position offset", null=False)


class Take(models.Model):
    quiz = models.ForeignKey(to=Quiz, on_delete=models.PROTECT, verbose_name="quiz id")
    user = models.ForeignKey(to=User, on_delete=models.PROTECT, verbose_name="user id")
    points = models.FloatField(_("points"))
    passage_date = models.DateField(_("passage date"), auto_now_add=True, null=False)
    id = models.BigAutoField(_("take id"), primary_key=True, auto_created=True, db_index=True)

    class Meta:
        verbose_name = _("take")
        verbose_name_plural = _("takes")
