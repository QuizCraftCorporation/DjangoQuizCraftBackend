"""
This module contains serializers for the quizzes app.
"""

import random
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import MCQQuestion, MCQOption, Question, Quiz, Take, TrueFalseQuestion


class QuizCreateSerializer(serializers.Serializer):
    """
    This serializer is used to create a new quiz.

    Attributes:
        quiz_name: The name of the quiz.
        source_name: The source of the quiz.
        max_questions: The maximum number of questions in the quiz.
        files: A list of files that contain the questions for the quiz.
        description: The description of the quiz.
        private: Whether the quiz is private.
    """
    quiz_name = serializers.CharField()
    source_name = serializers.CharField()
    max_questions = serializers.IntegerField(required=False)
    files = serializers.ListField(child=serializers.FileField())
    description = serializers.CharField(required=False)
    private = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        """
        Updates an instance of a model.

        Args:
            instance (Model): The model instance to update.
            validated_data (dict): The data to update the model instance with.

        Returns:
            Model: The updated model instance.
        """
        instance.creator = self.context.get("request").user.id
        instance.save()
        return instance


class GetQuizSerializer(serializers.Serializer):
    """
    Serializer for getting a quiz.

    Attributes:
        quiz_id (IntegerField): The ID of the quiz to get.
    """
    quiz_id = serializers.IntegerField()

    def validate_quiz_id(self, value):
        """
        Validates the quiz ID.

        Args:
            value (IntegerField): The ID of the quiz to get.

        Raises:
            ValidationError: If the quiz with the given ID does not exist.
        """
        try:
            # Check if the quiz with the given ID exists
            Quiz.objects.get(id=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invalid quiz ID.")


class QuizSerializer(serializers.ModelSerializer):
    """
    QuizSerializer

    This serializer is used to serialize a quiz.

    Attributes:
        questions: A list of questions in the quiz.
        title: The name of the quiz.
        description: The description of the quiz.
        private: Whether the quiz is private.
    """
    questions = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.CharField()
    private = serializers.BooleanField()

    class Meta:
        model = Quiz
        fields = ["id", "title", "questions", "description", "private"]

    def get_questions(self, obj: Quiz):
        """
        Get questions of the particular quiz

        Args:
            obj: The quiz we are getting questions from

        Returns:
            List of the questions in the quiz, serialized as `MCQQuestionSerializer` objects.
        """
        all_questions = obj.question_set.all()
        questions = [
            MCQQuestionSerializer(question.mcq_question).data
            for question in all_questions
        ]
        return questions

    def get_title(self, obj):
        """
        Get title of the particular quiz

        Args:
            obj: The quiz we are getting title from

        Returns:
            The title of the quiz.
        """
        return obj.name


class QuizMeSerializer(serializers.ModelSerializer):
    """
    Serializer for personal quizzes.
    """
    class Meta:
        model = Quiz
        fields = ['id', 'name', 'ready', 'description']


class QuizAnswersSerializer(QuizSerializer):
    """
    Serializer for a quiz with answers.
    """
    def get_questions(self, obj: Quiz):
        """
        Gets questions of the quiz.

        Args:
            obj (Quiz): The quiz to get the questions for.

        Returns:
            A list of serialized questions.
        """
        all_questions = obj.question_set.all()
        questions = [
            MCQQuestionAnswersSerializer(question.mcq_question).data
            for question in all_questions
        ]
        return questions


class MCQQuestionOptionSerializer(serializers.ModelSerializer):
    """
    Serializer for a multiple choice question option.
    """
    class Meta:
        model = MCQOption
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for a question.
    """
    class Meta:
        model = Question
        fields = ["id", "text"]


class MCQQuestionSerializer(serializers.ModelSerializer):
    """
    Serializer for a multiple choice question.
    """
    options = serializers.SerializerMethodField()
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = MCQQuestion
        fields = ["question", "options"]

    @staticmethod
    def get_options(obj):
        """
        Gets the options for the question.

        Args:
            obj (MCQQuestion): The question to get the options for.

        Returns:
            list: A list of serialized options.
        """
        all_options = obj.options.all()
        options = [
            MCQQuestionOptionSerializer(option, read_only=True).data
            for option in all_options
        ]
        random.shuffle(options)
        return options


class MCQQuestionAnswersSerializer(MCQQuestionSerializer):
    """
    Serializer for a multiple choice question with answers.
    """
    answers = serializers.SerializerMethodField()

    class Meta:
        model = MCQQuestion
        fields = MCQQuestionSerializer.Meta.fields + ["answers"]

    @staticmethod
    def get_answers(obj):
        """
        Gets the IDs of the correct options for the question.

        Args:
            obj (MCQQuestion): The question to get answers for.

        Returns:
            A list of the IDs of the correct options.
        """
        correct_option_ids = [option.id for option in obj.options.filter(correct__exact=True)]
        return correct_option_ids


class MCQUserAnswerSerializer(serializers.Serializer):
    """
    Serializer for answer on a question.

    Attributes:
        question_id (IntegerField): The ID of the question.
        user_answer (ListField): The list of IDs of the chosen options.
    """
    # Serializer for answer on a question
    question_id = serializers.IntegerField()
    user_answer = serializers.ListField(child=serializers.IntegerField())

    def run_validation(self, data=serializers.empty):
        """
        Checks the data and sets the `question_id` attribute.

        Args:
            data (dict): The data to validate.

        Returns:
            The validated data.
        """
        if data is serializers.empty:
            data = self.initial_data

        question_id = data.get('question_id')
        self.question_id = question_id

        return super().run_validation(data)

    @staticmethod
    def validate_question_id(value):
        """
        Validates the question ID.

        Args:
            value (int): The question ID.

        Returns:
            int: The validated question ID.

        Raises:
            ValidationError: If the question with the given ID does not exist.
        """
        try:
            # Check if the question with the given ID exists
            MCQQuestion.objects.get(pk=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invalid question ID.")

        return value

    def validate_chosen_option_ids(self, value):
        """
        Validates the chosen option IDs.

        Args:
            value (list): The list of chosen option IDs.

        Returns:
            The validated list of chosen option IDs.

        Raises:
            ValidationError: If the option with the given ID does not exist.
        """
        question_id = self.question_id
        question = MCQQuestion.objects.get(pk=question_id)
        question_option_set = set(question.options.all().values_list('id', flat=True))
        try:
            # Check if the MCQOptions with the given ID exists
            if any(opt_id not in question_option_set for opt_id in value):
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invalid chosen option IDs.")

        return value


class AnswerWithScoreSerializer(serializers.Serializer):
    """
    Serializer for answer on a question with a score.

    Attributes:
        question_id (IntegerField): The ID of the question.
        score (FloatField): The score of ths user for given question.
    """
    question_id = serializers.IntegerField()
    score = serializers.FloatField()


class MCQAnswerWithScoreSerializer(AnswerWithScoreSerializer):
    """
    Serializer for a multiple choice answer with a score.

    Attributes:
        user_answer (ListField): The list of ids of options chosen by the user.
        correct_answer (ListField): The list of ids of correct options.
    """
    user_answer = serializers.ListField(child=serializers.IntegerField())
    correct_answer = serializers.ListField(child=serializers.IntegerField())


class TrueFalseAnswerWithScoreSerializer(AnswerWithScoreSerializer):
    """
    Serializer for a true-false answer with a score.

    Attributes:
        user_answer (BooleanField): The option chosen by the user.
        correct_answer (BooleanField): The option of the correct option.
    """
    user_answer = serializers.BooleanField()
    correct_answer = serializers.BooleanField()


def get_scored_answer_serializer(question):
    """
    Get appropriate scored answer serializer for the particular question

    Args:
        question (Question): The question that wanted to be scored.

    Returns:
        The appropriate serializer for the scored answer.
    """
    if isinstance(question, MCQQuestion):
        return MCQAnswerWithScoreSerializer
    elif isinstance(question, TrueFalseQuestion):
        return TrueFalseAnswerWithScoreSerializer
    else:
        return AnswerWithScoreSerializer


class QuizResultSerializer(serializers.Serializer):
    """
     Serializer for quiz results.
     """
    scored_answers = serializers.SerializerMethodField()
    total_score = serializers.FloatField()
    quiz_id = serializers.IntegerField()

    def get_scored_answers(self, obj):
        """
        Get the list of scored answers.

        Args:
          obj (QuizResult): The quiz result object.

        Returns:
          A list of serialized scored answers.
        """
        initial_data = self.initial_data
        scored_answers = initial_data.get('scored_answers')
        serializer_data = []

        for answer in scored_answers:
            if isinstance(answer, MCQUserAnswerSerializer):
                serializer = MCQAnswerWithScoreSerializer
            else:
                serializer = AnswerWithScoreSerializer

            serializer_data.append(serializer(answer).data)

        return serializer_data


class QuizSubmissionSerializer(serializers.Serializer):
    """
    Serializer for quiz submissions.
    """
    # Serializer for quiz answers including multiple
    # questions
    answers = MCQUserAnswerSerializer(many=True)

    def create(self, validated_data):
        """
        Create a quiz submission.

        Args:
          validated_data (dict): The validated data from the serializer.

        Returns:
          A dictionary with information about quiz submission (scored answers, quiz id, total score).
        """
        user = self.context.get("user")
        quiz = self.context.get("quiz")
        total = 0
        answers_with_score = []  # List for scored answers
        for answer in validated_data.get('answers'):
            basic_question = \
                Question.objects.get(pk=answer.get("question_id"))
            question = basic_question.get_question_with_type()  # Question with specific type
            question_answer = question.get_answer()  # Answer on the question
            evaluator_type = question.get_evaluator()  # Evaluator for specific question
            evaluator = evaluator_type(question_answer)  # Evaluator instance
            score = evaluator.evaluate(answer.get("user_answer"))  # Score of the user answer
            total += score  # Adding score to the total score of user in quiz
            answer.update(
                {
                    'correct_answer': question_answer,
                    'score': score
                }
            )  # Adding score and correct answer to give answer by user
            answer_with_score_serializer_type = get_scored_answer_serializer(question)
            answer_with_score_serializer = answer_with_score_serializer_type(answer)
            answers_with_score.append(answer_with_score_serializer.data)
        take = Take(quiz=quiz, user=user, points=total)  # Instantiating model for the quiz take
        take.save()  # Adding this try to database
        return {
            "scored_answers": answers_with_score,
            "quiz_id": quiz.id,
            "total_score": total
        }
