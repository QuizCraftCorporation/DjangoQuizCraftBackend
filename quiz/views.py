import random
from datetime import datetime

from celery.result import AsyncResult
from django.core.cache import cache
from django.db.models import Count, Max, Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

# View class for registration
from rest_framework.viewsets import ViewSet

from app.settings import SEARCH_DB, env
from quiz.models import Material, Quiz, QuizView, Take
from quiz.serializers import (
    GetQuizSerializer,
    QuizAnswersSerializer,
    QuizCreateSerializer,
    QuizMeSerializer,
    QuizSerializer,
    QuizSubmissionSerializer,
)
from quiz.tasks import create_quiz


def sort_by_views(queryset_init, start_date, end_date):
    queryset = queryset_init
    ids = queryset.values_list("id", flat=True)
    views = QuizView.objects.filter(quiz_id__in=ids)
    if start_date:
        views = views.filter(viewed_at__gte=start_date)
    if end_date:
        views = views.filter(viewed_at__lte=end_date)
    sorted_views = (
        views.values("quiz_id")
        .annotate(count=Count("quiz_id"))
        .order_by("-count")
    )
    target_ids = sorted_views.values_list("quiz_id", flat=True)
    bulk = Quiz.objects.in_bulk(target_ids)
    queryset = [
        bulk[pk] for pk in target_ids
    ]  # Sorting by views in descending order
    return queryset


def sort_by_unique_views(queryset_init, start_date, end_date):
    queryset = queryset_init
    ids = queryset.values_list("id", flat=True)
    views = QuizView.objects.filter(quiz_id__in=ids)
    if start_date:
        views = views.filter(viewed_at__gte=start_date)
    if end_date:
        views = views.filter(viewed_at__lte=end_date)
    sorted_views = (
        views.values("quiz_id")
        .annotate(count=Count("viewer_id", distinct=True))
        .order_by("-count")
    )
    target_ids = sorted_views.values_list(
        "quiz_id", flat=True
    ).distinct()
    bulk = Quiz.objects.in_bulk(target_ids)
    queryset = [bulk[pk] for pk in target_ids]
    return queryset


def sort_by_passes(queryset_init, start_date, end_date):
    queryset = queryset_init
    takes = Take.objects.filter(
        quiz__creator__id__in=queryset.values("id")
    )
    if start_date:
        takes = takes.filter(passage_date__gte=start_date)
    if end_date:
        takes = takes.filter(passage_date__lte=end_date)
    queryset = (
        takes.values("quiz_id")
        .annotate(count=Count("quiz_id"))
        .order_by("-count")
    )  # Sorting by passes in descending order
    target_ids = queryset.values_list("quiz_id", flat=True)
    bulk = Quiz.objects.in_bulk(target_ids)
    queryset = [bulk[pk] for pk in target_ids]
    return queryset


class QuizViewSet(ViewSet):
    """
    View set for working with Quiz model instances in database.
    """

    @action(
        detail=False, methods=["get"], permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        """
        Get list of quizzes for current user.
        """
        sort = request.query_params.get("sort")
        if sort == "last_viewed":
            views = QuizView.objects.filter(viewer__exact=request.user)
            # Filtering by start and end dates
            start_date = request.query_params.get("start_date")
            end_date = request.query_params.get("end_date")
            if start_date:
                views = QuizView.objects.filter(viewed_at__gte=start_date)
            if end_date:
                views = QuizView.objects.filter(viewed_at__lte=end_date)
            queryset = (
                views.values_list("quiz_id", flat=True)  # Get list of quiz ids
                .annotate(  # Save id from each group with
                    # maximal viewed at time
                    latest_viewed_at=Max("viewed_at")
                )
                .order_by(  # Order the single quizzes from each group by
                    # last viewed time in reversed order
                    "-latest_viewed_at"
                )
            )
            offset = int(request.query_params.get("offset", 0))
            limit = int(request.query_params.get("limit", 10))
            queryset = queryset[offset: offset + limit]
            bulk = Quiz.objects.in_bulk(queryset)
            queryset = [bulk[pk] for pk in queryset]
        else:
            queryset = Quiz.objects.filter(
                creator__exact=request.user
            ).order_by("ready", "-created_at")
        serializer = QuizMeSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def random(self, request):
        queryset = Quiz.objects.filter(
            Q(private__exact=False) | Q(creator__exact=request.user.id),
            ready__exact=True,
        )
        if not queryset:
            return JsonResponse(
                {"detail": "No available quizzes for you."},
                status=status.HTTP_404_NOT_FOUND,
            )
        random_quiz = random.choice(queryset.all())
        if request.query_params.get("answer") is True:
            quiz_serializer = QuizAnswersSerializer(
                random_quiz
            )  # Serializer for answer request
        else:
            quiz_serializer = QuizSerializer(
                random_quiz
            )  # Serializer for simple quiz request
        return Response(quiz_serializer.data)

    def list(self, request):
        """
        Get list of quizzes for given query parameters.
        """

        queryset = Quiz.objects.filter(
            Q(private__exact=False) | Q(creator__exact=request.user.id)
        )
        # Filtering by start and end dates
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
            queryset = queryset.filter(created_at__lte=end_date)

        # Sorting
        sort_algorithm = request.query_params.get("sort")
        if sort_algorithm == "views":
            queryset = sort_by_views(queryset, start_date, end_date)
        elif sort_algorithm == "unique_views":
            queryset = sort_by_unique_views(queryset, start_date, end_date)
        elif sort_algorithm == "passes":
            queryset = sort_by_passes(queryset, start_date, end_date)
        elif sort_algorithm == "generations":
            queryset = queryset.filter(ready__exact=True).order_by(
                "-created_at"
            )

        # Pagination
        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 10))
        queryset = queryset[offset: offset + limit]

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
                    "ids": [
                        processing_quizz.id
                        for processing_quizz in processing_quizzes
                    ],
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        materials = []
        max_questions = serializer.validated_data.get("max_questions")
        name = serializer.validated_data["quiz_name"]
        optional = {
            "description": serializer.validated_data["description"]
            if "description" in serializer.validated_data
            else "",
            "private": serializer.validated_data["private"]
            if "private" in serializer.validated_data
            else False,
        }
        quiz = Quiz.objects.create(name=name, creator=request.user, **optional)
        for file in serializer.validated_data["files"]:
            new_material = Material.objects.create(
                name=serializer.validated_data["source_name"], file=file
            )
            new_material.quiz_set.add(quiz)
            materials.append(new_material)
        file_names = [str(material.file.file) for material in materials]

        task = create_quiz.delay(
            file_names, quiz.pk, max_questions, optional["description"]
        )
        cache.set(quiz.id, task.id, 18000)
        return Response(
            {"detail": "Quiz on creation stage", "id": quiz.id},
            status=status.HTTP_200_OK,
        )

    @permission_classes([IsAuthenticatedOrReadOnly])
    def retrieve(self, request, pk=None, **kwargs):
        answer = True if request.query_params.get("answer") else False
        get_quiz_serializer = GetQuizSerializer(data={"quiz_id": pk})
        get_quiz_serializer.is_valid(raise_exception=True)
        quiz = Quiz.objects.filter(pk=pk).first()
        if quiz.private and quiz.creator != request.user:
            return JsonResponse(
                {
                    "detail": "This quiz is private and "
                    "cannot be accessed by you."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        if not quiz.ready:
            return JsonResponse(
                {"detail": "This quiz is not ready yet."},
                status=status.HTTP_425_TOO_EARLY,
            )
        if answer:
            quiz_serializer = QuizAnswersSerializer(
                quiz
            )  # Serializer for answer request
        else:
            quiz_serializer = QuizSerializer(
                quiz
            )  # Serializer for simple quiz request
        if request.user.id:
            quiz.view(request.user.id)
            quiz.save()
        return Response(quiz_serializer.data)

    @action(
        detail=False,
        methods=["get"],
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def check_generation(self, request):
        not_ready_quizzes = request.user.quizzes.filter(ready__exact=False)
        if not_ready_quizzes:
            return JsonResponse(
                {
                    "detail": "You have quizzes already generating for you.",
                    "quizzes": list(
                        not_ready_quizzes.values_list("id", flat=True)
                    ),
                },
                status=status.HTTP_425_TOO_EARLY,
            )
        return JsonResponse(
            {"detail": "You have no quizzes generating for you."},
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        permission_classes=[IsAuthenticatedOrReadOnly],
    )
    def check_progress(self, request, pk=None):
        if pk:
            quiz = Quiz.objects.filter(pk=pk).first()
            if not quiz:
                return JsonResponse(
                    {"detail": "Quiz does not exist!"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if quiz.creator != request.user:
                return JsonResponse(
                    {"detail": "Access to this quiz is not allowed for you!"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            task_id = cache.get(pk, None)
            if task_id:
                task = AsyncResult(task_id)

                if task.state == "FAILURE" or task.state == "PENDING":
                    response = {
                        "id": pk,
                        "state": task.state,
                        "progress": 0,
                    }
                    return JsonResponse(response, status=200)
                current = task.info.get("current", 0)
                total = task.info.get("total", 1)
                progress = (
                    int(current) / int(total)
                ) * 100  # to display a percentage of progress of the task
                response = {
                    "id": pk,
                    "state": task.state,
                    "progress": progress,
                }
                return JsonResponse(response, status=200)
            return JsonResponse(
                {"detail": "No tasks are associated with given quiz id!"},
                status=status.HTTP_404_NOT_FOUND,
            )
        return JsonResponse(
            {"detail": "No quiz id was provided!"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=False, methods=["get"])
    def search(self, request):
        search_data = request.query_params.get("data")
        if not search_data:
            return JsonResponse(
                {"detail": "You have no text to search with."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            results = SEARCH_DB.search_quiz(
                search_data,
                number_of_results=int(
                    env("NUMBER_OF_SEARCH_RESULTS", default=10)
                ),
            )
        except Exception as e:
            print(e.__str__())
            return JsonResponse(
                {"detail": "Database is empty."},
                status=status.HTTP_409_CONFLICT,
            )
        ids = [int(result[1]) for result in results]
        queryset = Quiz.objects.filter(
            Q(private__exact=False) | Q(creator__exact=request.user.id)
        ).in_bulk(ids)
        result_list = [queryset[pk] for pk in ids if queryset.get(pk)]
        serializer = QuizMeSerializer(result_list, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated]
    )
    def attempt(self, request, pk=None):
        quiz = get_object_or_404(Quiz, pk=pk)
        serializer = QuizSubmissionSerializer(
            data=self.request.data,
            context={"user": request.user, "quiz": quiz},
        )
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save())
