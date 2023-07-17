import random
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers

from .models import MCQQuestion, MCQOption, Question, Quiz, Take, TrueFalseQuestion


class QuizCreateSerializer(serializers.Serializer):
    quiz_name = serializers.CharField()
    source_name = serializers.CharField()
    max_questions = serializers.IntegerField(required=False)
    files = serializers.ListField(child=serializers.FileField())
    description = serializers.CharField(required=False)
    private = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        instance.creator = self.context.get("request").user.id
        instance.save()
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
    description = serializers.CharField()
    private = serializers.BooleanField()

    class Meta:
        model = Quiz
        fields = ["id", "title", "questions", "description", "private"]

    def get_questions(self, obj: Quiz):
        all_questions = obj.question_set.all()
        questions = [
            MCQQuestionSerializer(question.mcq_question).data
            for question in all_questions
        ]
        return questions

    def get_title(self, obj):
        return obj.name


class QuizMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'name', 'ready', 'description']


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
        fields = MCQQuestionSerializer.Meta.fields + ["answers"]

    @staticmethod
    def get_answers(obj):
        correct_option_ids = [option.id for option in obj.options.filter(correct__exact=True)]
        return correct_option_ids


class MCQUserAnswerSerializer(serializers.Serializer):
    # Serializer for answer on a question
    question_id = serializers.IntegerField()
    user_answer = serializers.ListField(child=serializers.IntegerField())

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
    score = serializers.FloatField()


class MCQAnswerWithScoreSerializer(AnswerWithScoreSerializer):
    user_answer = serializers.ListField(child=serializers.IntegerField())
    correct_answer = serializers.ListField(child=serializers.IntegerField())


class TrueFalseAnswerWithScoreSerializer(AnswerWithScoreSerializer):
    user_answer = serializers.BooleanField()
    correct_answer = serializers.BooleanField()


def get_scored_answer_serializer(question):
    if isinstance(question, MCQQuestion):
        return MCQAnswerWithScoreSerializer
    elif isinstance(question, TrueFalseQuestion):
        return TrueFalseAnswerWithScoreSerializer
    else:
        return AnswerWithScoreSerializer


class QuizResultSerializer(serializers.Serializer):
    scored_answers = serializers.SerializerMethodField()
    total_score = serializers.FloatField()
    quiz_id = serializers.IntegerField()

    def get_scored_answers(self, obj):
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
    # Serializer for quiz answers including multiple
    # questions
    answers = MCQUserAnswerSerializer(many=True)

    def create(self, validated_data):
        user = self.context.get("user")
        quiz = self.context.get("quiz")
        total = 0
        answers_with_score = []  # List for scored answers
        for answer in validated_data.get('answers'):
            basic_question = \
                Question.objects.get(pk=answer.get("question_id"))
            question = basic_question.get_question_with_type()  # Question with specific type
            evaluator_type = question.get_evaluator()  # Evaluator for specific question
            evaluator = evaluator_type(question)  # Evaluator instance
            score = evaluator.evaluate(answer.get("user_answer"))  # Score of the user answer
            total += score  # Adding score to the total score of user in quiz
            answer.update(
                {
                    'correct_answer': question.get_answer(),
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
