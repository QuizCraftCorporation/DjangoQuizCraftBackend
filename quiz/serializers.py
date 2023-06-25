import random

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import MCQQuestion, MCQOption, Question, Quiz, Take
from .quiz_evaluation import MCQQuestionBinaryEvaluator


class QuizCreateSerializer(serializers.Serializer):
    quiz_name = serializers.CharField()
    source_name = serializers.CharField()
    files = serializers.ListField(child=serializers.FileField())

    def update(self, instance, validated_data):
        instance.creator = self.context.get("request").user.id
        return instance


class GetQuizSerializer(serializers.Serializer):
    quiz_id = serializers.IntegerField()

    def validate_quiz_id(self, value):
        try:
            # Check if the quiz with the given ID exists
            Quiz.objects.get(id=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invalid quiz ID.")


class QuizSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ["id", "title", "questions"]

    def get_questions(self, obj: Quiz):
        all_questions = obj.question_set.all()
        questions = [
            MCQQuestionSerializer(question.mcq_question).data
            for question in all_questions
        ]
        return questions

    def get_title(self, obj):
        return obj.name


class QuizAnswersSerializer(QuizSerializer):
    def get_questions(self, obj: Quiz):
        all_questions = obj.question_set.all()
        questions = [
            MCQQuestionAnswersSerializer(question.mcq_question).data
            for question in all_questions
        ]
        return questions


class MCQQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCQOption
        fields = ["id", "text"]


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "text"]


class MCQQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    question = QuestionSerializer(read_only=True)

    class Meta:
        model = MCQQuestion
        fields = ["question", "options"]

    @staticmethod
    def get_options(obj):
        all_options = obj.options.all()
        options = [
            MCQQuestionOptionSerializer(option, read_only=True).data
            for option in all_options
        ]
        random.shuffle(options)
        return options

    @staticmethod
    def get_answer(obj):
        return obj.answer.text


class MCQQuestionAnswersSerializer(MCQQuestionSerializer):
    answer = serializers.SerializerMethodField()

    class Meta:
        model = MCQQuestion
        fields = ["question", "options", "answer"]

    def get_answer(self, obj):
        return obj.answer.text


class UserAnswerSerializer(serializers.Serializer):
    # Serializer for answer on a question
    question_id = serializers.IntegerField()
    chosen_option_id = serializers.IntegerField()

    def run_validation(self, data=serializers.empty):
        if data is serializers.empty:
            data = self.initial_data

        question_id = data.get('question_id')
        self.question_id = question_id

        return super().run_validation(data)

    @staticmethod
    def validate_question_id(value):
        try:
            # Check if the question with the given ID exists
            MCQQuestion.objects.get(pk=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invalid question ID.")

        return value

    def validate_chosen_option_id(self, value):
        question_id = self.question_id
        try:
            # Check if the MCQOption with the given ID exists
            option = MCQOption.objects.get(pk=value)
            if option.question.question.id != question_id:
                raise ObjectDoesNotExist
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invalid chosen option ID.")

        return value


class AnswerWithScoreSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    correct_answer_id = serializers.IntegerField()
    score = serializers.FloatField()


class QuizResultSerializer(serializers.Serializer):
    scored_answers = AnswerWithScoreSerializer(many=True)
    total_score = serializers.FloatField()
    quiz_id = serializers.IntegerField()


class QuizSubmissionSerializer(serializers.Serializer):
    # Serializer for quiz answers including multiple
    # questions
    quiz_id = serializers.IntegerField()
    answers = UserAnswerSerializer(many=True)

    @staticmethod
    def validate_quiz_id(value):
        try:
            # Check if the quiz with the given ID exists
            Quiz.objects.get(pk=value)
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Invalid quiz ID.")

        return value

    def create(self, validated_data):
        user = self.context.get("user")
        quiz = Quiz.objects.get(pk=validated_data.get("quiz_id"))
        total = 0
        answers_with_score = []
        for answer in validated_data.get('answers'):
            question = MCQQuestion.objects.get(pk=answer.get("question_id"))
            question_answer = question.answer
            score = MCQQuestionBinaryEvaluator.evaluate(question, answer.get("chosen_option_id"))
            total += score
            answer_with_score = {"question_id": answer.get("question_id"), "correct_answer_id": question_answer.id,
                                 "score": score}
            answers_with_score.append(answer_with_score)
        Take.objects.create(quiz=quiz, user=user, points=total)
        quiz_result_serializer = QuizResultSerializer(data={"scored_answers": answers_with_score,
                                                            "quiz_id": validated_data.get("quiz_id"),
                                                            "total_score": total})
        quiz_result_serializer.is_valid()
        return quiz_result_serializer.data
