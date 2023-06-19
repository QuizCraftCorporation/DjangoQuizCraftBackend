import random

from rest_framework import serializers

from .models import MCQQuestion, MCQOption, Question, Quiz


class QuizCreateSerializer(serializers.Serializer):
    quiz_name = serializers.CharField()
    source_name = serializers.CharField()
    file = serializers.FileField()

    def update(self, instance, validated_data):
        instance.creator = self.context.get("request").user.id
        return instance


class QuizSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ["id", "title", "questions"]

    def get_questions(self, obj: Quiz):
        all_questions = obj.question_set.all()
        questions = [
            MCQQuestionSerializer(question.MCQQuestion).data
            for question in all_questions
        ]
        return questions

    def get_title(self, obj):
        return obj.name


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
    answer = serializers.SerializerMethodField()

    class Meta:
        model = MCQQuestion
        fields = ["question", "options", "answer"]

    def get_options(self, obj):
        all_options = obj.options.all()
        options = [
            MCQQuestionOptionSerializer(option, read_only=True).data
            for option in all_options
        ]
        random.shuffle(options)
        return options

    def get_answer(self, obj):
        return obj.answer.text

