from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

# View class for registration
from QuizGeneratorModel.quiz_craft_package.quiz_generator import QuizGenerator
from quiz.models import Material, Quiz
from quiz.serializers import QuizCreateSerializer, QuizSerializer, QuizSubmissionSerializer


class QuizCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        material = Material.objects.create(name=serializer.validated_data["source_name"],
                                           file=serializer.validated_data["file"])
        name = serializer.validated_data["quiz_name"]
        quiz = Quiz.objects.create(name=name, creator=request.user)
        material.quiz_set.add(quiz)
        quiz_gen = QuizGenerator(debug=False)
        result = quiz_gen.create_questions_from_files([str(material.file.file)])
        quiz.add_questions(result)
        return Response(QuizSerializer(quiz).data)


class QuizView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        quiz = Quiz.objects.get(id=id)
        return Response(QuizSerializer(quiz).data)


class QuizEvaluate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = QuizSubmissionSerializer(data=self.request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())
