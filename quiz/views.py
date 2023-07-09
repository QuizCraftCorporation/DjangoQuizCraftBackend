from datetime import datetime

from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, Count
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
# View class for registration
from rest_framework.viewsets import ViewSet

from app.settings import SEARCH_DB, env
from quiz.models import Material, Quiz, Take, QuizView
from quiz.serializers import QuizAnswersSerializer, QuizCreateSerializer, QuizSerializer, QuizSubmissionSerializer, \
    GetQuizSerializer, QuizMeSerializer
from quiz.tasks import create_quiz


class QuizViewSet(ViewSet):
    """
    View set for working with Quiz model instances in database.
    """

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get list of quizzes for current user.
        """
        sort = request.query_params.get('sort')
        print(sort)
        if sort == 'last_viewed':
            views = QuizView.objects.filter(viewer_id__exact=request.user.id)
            # Filtering by start and end dates
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            if start_date:
                views = QuizView.objects.filter(viewed_at__gte=start_date)
            if end_date:
                views = QuizView.objects.filter(viewed_at__lte=end_date)
            quizzes = views.order_by('-viewed_at')
            offset = int(request.query_params.get('offset', 0))
            limit = int(request.query_params.get('limit', 10))
            queryset = quizzes.values_list('quiz_id', flat=True).distinct()  # Add distinct() to remove duplicates
            queryset = queryset[offset:offset + limit]
            bulk = Quiz.objects.in_bulk(queryset)
            # result = []
            # for pk in queryset:
            #     if not bulk:
            #         queryset = {}
            #     if pk in bulk:
            #         result.append(bulk[pk])
            #         bulk.pop(pk)
            queryset = [bulk[pk] for pk in queryset]
        else:
            queryset = request.user.quizzes.filter(ready__exact=True)
        serializer = QuizMeSerializer(queryset, many=True)
        return Response(serializer.data)

    def list(self, request):
        """
        Get list of quizzes for given query parameters.
        """

        queryset = Quiz.objects.filter(
            Q(private__exact=False) |
            Q(creator__exact=request.user.id)
        )
        # Filtering by start and end dates
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            queryset = queryset.filter(created_at__lte=end_date)

        # Sorting
        sort_algorithm = request.query_params.get('sort')
        if sort_algorithm == 'views':
            ids = queryset.values_list('id', flat=True)
            views = QuizView.objects.filter(quiz_id__in=ids)
            if start_date:
                views = views.filter(viewed_at__gte=start_date)
            if end_date:
                views = views.filter(viewed_at__lte=end_date)
            sorted_views = views.values('quiz_id').annotate(count=Count('quiz_id')).order_by('-count')
            target_ids = sorted_views.values_list('quiz_id', flat=True)
            bulk = Quiz.objects.in_bulk(target_ids)
            queryset = [bulk[pk] for pk in target_ids]  # Sorting by views in descending order
        elif sort_algorithm == 'unique_views':
            ids = queryset.values_list('id', flat=True)
            views = QuizView.objects.filter(quiz_id__in=ids)
            if start_date:
                views = views.filter(viewed_at__gte=start_date)
            if end_date:
                views = views.filter(viewed_at__lte=end_date)
            sorted_views = views.values('quiz_id').annotate(
                count=Count('viewer_id', distinct=True)
            ).order_by('-count')
            target_ids = sorted_views.values_list('quiz_id', flat=True).distinct()
            bulk = Quiz.objects.in_bulk(target_ids)
            queryset = [bulk[pk] for pk in target_ids]
        elif sort_algorithm == 'passes':
            takes = Take.objects.filter(quiz__creator__id__in=queryset.values("id"))
            if start_date:
                takes = takes.filter(passage_date__gte=start_date)
            if end_date:
                takes = takes.filter(passage_date__lte=end_date)
            queryset = takes.values('quiz_id').annotate(count=Count('quiz_id')).order_by(
                '-count')  # Sorting by passes in descending order
            target_ids = queryset.values_list('quiz_id', flat=True)
            bulk = Quiz.objects.in_bulk(target_ids)
            queryset = [bulk[pk] for pk in target_ids]
        elif sort_algorithm == 'generations':
            queryset = queryset.filter(ready__exact=True).order_by('-created_at')

        # Pagination
        offset = int(request.query_params.get('offset', 0))
        limit = int(request.query_params.get('limit', 10))
        queryset = queryset[offset:offset + limit]

        serializer = QuizMeSerializer(queryset, many=True)
        return Response(serializer.data)

    @permission_classes([IsAuthenticated])
    def create(self, request):
        """
        Create new quiz using QuizGeneratorModel submodule.
        """
        processing_quizzes = request.user.quizzes.filter(ready__exact=False)
        if processing_quizzes:
            return JsonResponse(
                {
                    "detail": "You have quiz already generating for you.",
                    "ids": [processing_quizz.id for processing_quizz in processing_quizzes]
                },
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        materials = []
        max_questions = serializer.validated_data.get("max_questions")
        name = serializer.validated_data["quiz_name"]
        optional = {
            "description": serializer.validated_data[
                "description"
            ] if "description" in serializer.validated_data else "",
            "private": serializer.validated_data[
                "private"
            ] if "private" in serializer.validated_data else False
        }
        quiz = Quiz.objects.create(name=name, creator=request.user, **optional)
        for file in serializer.validated_data["files"]:
            new_material = Material.objects.create(name=serializer.validated_data["source_name"],
                                                   file=file)
            new_material.quiz_set.add(quiz)
            materials.append(new_material)
        file_names = [str(material.file.file) for material in materials]
        create_quiz.delay(file_names, quiz.pk, max_questions, optional["description"])
        return Response(
            {
                "detail": "Quiz on creation stage",
                "id": quiz.id
            }, status=status.HTTP_200_OK
        )

    def retrieve(self, request, pk=None, **kwargs):
        answer = True if request.query_params.get('answer') else False
        get_quiz_serializer = GetQuizSerializer(data={"quiz_id": pk})
        get_quiz_serializer.is_valid(raise_exception=True)
        quiz = Quiz.objects.get(pk=pk)
        if request.user is not AnonymousUser:
            quiz.view(request.user.id)
        quiz.save()
        if quiz.private and quiz.creator != request.user:
            return JsonResponse(
                {
                    "detail": "This quiz is private and cannot be accessed by you."},
                status=status.HTTP_403_FORBIDDEN
            )
        if not quiz.ready:
            return JsonResponse(
                {
                    "detail": "This quiz is not ready yet."
                },
                status=status.HTTP_425_TOO_EARLY
            )
        if answer:
            quiz_serializer = QuizAnswersSerializer(quiz)  # Serializer for answer request
        else:
            quiz_serializer = QuizSerializer(quiz)  # Serializer for simple quiz request
        return Response(quiz_serializer.data)

    @action(detail=False, methods=['get'])
    def search(self, request):
        # TODO fix the error with vector db connection
        search_data = request.data['data']
        results = SEARCH_DB.search_quiz(search_data,
                                        number_of_results=int(env('NUMBER_OF_SEARCH_RESULTS', default=10)))
        ids = [result[1] for result in results]
        queryset = Quiz.objects.filter(id__in=ids)
        serializer = QuizMeSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def attempt(self, request, pk=None):
        quiz = get_object_or_404(Quiz, pk=pk)
        serializer = QuizSubmissionSerializer(data=self.request.data, context={'user': request.user, 'quiz': quiz})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())
