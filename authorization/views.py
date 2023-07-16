from datetime import timedelta

from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer
from rest_framework_simplejwt.views import TokenRefreshView

from authorization.serializers import UserRegisterSerializer, UserSerializer


# View class for registration
class RegisterView(APIView):
    """
        This view class is used to register new users.

        Args:
            request: The HTTP request object with data required for registration.

        Returns:
            A JSON response containing the data of the newly created user.
    """
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserInfoView(APIView):
    """
        This view class is used to get the information of the authenticated user.

        Args:
            request: The HTTP request object.

        Returns:
            A JSON response containing the data of the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class RefreshView(TokenRefreshView):
    """
    This view class is used to refresh the user's token and save it in database. This class is recommended to be
    used when Blacklist After Rotation is required.

    Args:
        request: The HTTP request object.

    Returns:
        A JSON response containing the new token.

    Todo:
        fix doubling of tokens in outstanding_tokens database table
    """

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data['refresh']
        tokens = OutstandingToken.objects.filter(token=request.data['refresh'])
        token = OutstandingToken.objects.create(
            user=tokens[0].user,
            token=refresh_token,
            expires_at=timezone.now() + timedelta(days=14),
            jti=get_random_string(length=32)
        )
        token.save()
        return response


class LogoutView(APIView):
    """
    This view class is used to log out the user.

    Args:
        request: The HTTP request object.

    Returns:
        A JSON response with status code 205.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            serializer = TokenBlacklistSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    """
    This view class is used to log out all the user's tokens.

    Args:
        request: The HTTP request object.

    Returns:
        A JSON response with status code 205.
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)
