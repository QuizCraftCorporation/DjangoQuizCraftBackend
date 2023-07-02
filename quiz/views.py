from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
# View class for registration
from rest_framework.viewsets import ViewSet

from QuizGeneratorModel.quiz_craft_package.quiz_generator import QuizGenerator
from quiz.models import Material, Quiz
from quiz.serializers import QuizAnswersSerializer, QuizCreateSerializer, QuizSerializer, QuizSubmissionSerializer, \
    GetQuizSerializer, QuizMeSerializer


class QuizViewSet(ViewSet):
    """
    View set for working with Quiz model instances in database.
    """

    @permission_classes([IsAuthenticated])
    def list(self, request):
        """
        Get list of quizzes for current user.
        """
        queryset = request.user.quizzes
        serializer = QuizMeSerializer(queryset, many=True)
        return Response(serializer.data)

    @permission_classes([IsAuthenticated])
    def create(self, request):
        """
        Create new quiz using QuizGeneratorModel submodule.
        """
        if request.user.quizzes.filter(ready__exact=True):
            return JsonResponse({"detail": "You have quiz already generating for you."},
                                status=status.HTTP_403_FORBIDDEN)
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        materials = []
        max_questions = serializer.validated_data.get("max_questions")
        name = serializer.validated_data["quiz_name"]
        quiz = Quiz.objects.create(name=name, creator=request.user)
        for file in serializer.validated_data["files"]:
            new_material = Material.objects.create(name=serializer.validated_data["source_name"],
                                                   file=file)
            new_material.quiz_set.add(quiz)
            materials.append(new_material)
        quiz_gen = QuizGenerator(debug=False)
        if max_questions:
            result = quiz_gen.create_questions_from_files([str(material.file.file) for material in materials],
                                                          max_questions=max_questions)
        else:
            result = quiz_gen.create_questions_from_files([str(material.file.file) for material in materials])
        quiz.add_questions(result)
        return Response(QuizSerializer(quiz).data)

    def retrieve(self, request, pk=None, **kwargs):
        answer = True if request.query_params.get('answer') else False
        get_quiz_serializer = GetQuizSerializer(data={"quiz_id": pk})
        get_quiz_serializer.is_valid(raise_exception=True)
        quiz = Quiz.objects.get(pk=pk)
        if quiz.private and quiz.creator != request.user:
            return JsonResponse({"detail": "This quiz is private and cannot be accessed by you."},
                                status=status.HTTP_403_FORBIDDEN)
        if not quiz.ready:
            return JsonResponse({"detail": "This quiz is not ready yet."},
                                status=status.HTTP_403_FORBIDDEN)
        if answer:
            quiz_serializer = QuizAnswersSerializer(quiz)  # Serializer for answer request
        else:
            quiz_serializer = QuizSerializer(quiz)  # Serializer for simple quiz request
        return Response(quiz_serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def attempt(self, request, pk=None):
        quiz = get_object_or_404(Quiz, pk=pk)
        serializer = QuizSubmissionSerializer(data=self.request.data, context={'user': request.user, 'quiz': quiz})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())
