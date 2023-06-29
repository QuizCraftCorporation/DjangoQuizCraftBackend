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


class MCQQuestionAnswersSerializer(MCQQuestionSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = MCQQuestion
        fields = ["question", "options", "answers"]

    @staticmethod
    def get_answers(obj):
        correct_option_ids = [option.id for option in obj.options.filter(correct__exact=True)]
        return correct_option_ids


class UserAnswerSerializer(serializers.Serializer):
    # Serializer for answer on a question
    question_id = serializers.IntegerField()
    chosen_option_ids = serializers.ListField(child=serializers.IntegerField())

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

    def validate_chosen_option_ids(self, value):
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
    question_id = serializers.IntegerField()
    chosen_option_ids = serializers.ListField(child=serializers.IntegerField())
    correct_answers_id = serializers.ListField(child=serializers.IntegerField())
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
            question = \
                MCQQuestion.objects.get(pk=answer.get("question_id"))
            question_answers = [
                option.id for option
                in question.options.filter(correct__exact=True)
            ]
            evaluator = MCQQuestionBinaryEvaluator(set(question_answers))
            score = evaluator.evaluate(answer.get("chosen_option_ids"))
            total += score
            answer_with_score = {
                "question_id": answer.get("question_id"),
                "correct_answer_ids": question_answers,
                "score": score,
                "chosen_option_ids": answer.get("chosen_option_ids")
            }
            answers_with_score.append(answer_with_score)
        take = Take(quiz=quiz, user=user, points=total)
        take.save()
        quiz_result_serializer = QuizResultSerializer(data={"scored_answers": answers_with_score,
                                                            "quiz_id": validated_data.get("quiz_id"),
                                                            "total_score": total})
        quiz_result_serializer.is_valid()
        return quiz_result_serializer.data
