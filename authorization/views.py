"""
Description: This module contains the view classes for user registration, user information, token refresh, and logging
    out.

Classes:

    RegisterView: This view class is used to register new users.
    UserInfoView: This view class is used to get the information of the authenticated user.
    RefreshView: This view class is used to refresh the user's token and save it in the database.
    LogoutView: This view class is used to log out the user.
    LogoutAllView: This view class is used to log out all the user's tokens.

Imports:

    datetime: This module provides the timedelta class, which is used to calculate the expiration date of the token.
    django.utils: This module provides the timezone and crypto modules, which are used to get the current time and
        generate a random string.
    rest_framework.permissions: This module provides the IsAuthenticated permission, which is used to ensure that the
        user is authenticated before they can access the views.
    rest_framework_simplejwt.token_blacklist.models: This module provides the OutstandingToken and BlacklistedToken
        models, which are used to store the user's tokens.
    rest_framework.response: This module provides the Response class, which is used to return a JSON response.
    rest_framework.views: This module provides the APIView class, which is the base class for all view classes in
        REST framework.
    rest_framework.status: This module provides the status constants, which are used to set the status code of the
        response.
    rest_framework_simplejwt.serializers: This module provides the TokenBlacklistSerializer serializer, which is used
        to serialize the token blacklist data.
    rest_framework_simplejwt.views: This module provides the TokenRefreshView class, which is used to refresh
        the user's token.

Serializers:

    UserRegisterSerializer: This serializer is used to serialize the user registration data.
    UserSerializer: This serializer is used to serialize the user information data.
"""

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
    """
    def post(self, request):
        """
        Register a new user.

        Args:
            request: The HTTP request object with data required for registration.

        Returns:
            A JSON response containing the data of the newly created user.

        Raises:
            ValidationError: If the request data is invalid.
        """
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserInfoView(APIView):
    """
        This view class is used to get the information of the authenticated user.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Gets the information of the authenticated user.

        Args:
            request: The HTTP request object.

        Returns:
            A JSON response containing the data of the authenticated user.

        Raises:
            ValidationError: If the request data is invalid.
            PermissionDenied: If the user is not authenticated.
       """
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class RefreshView(TokenRefreshView):
    """
    This view class is used to refresh the user's token and save it in database. This class is recommended to be
    used when Blacklist After Rotation is required.
    """

    def post(self, request, *args, **kwargs):
        """
        Refreshes the user's token and saves it in the database.

        Args:
            request: The HTTP request object.

        Returns:
            A JSON response containing the new token.

        Todo:
            fix doubling of tokens in outstanding_tokens database table
       """
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
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Logs out the user.

        Args:
            request: The HTTP request object.

        Returns:
            A JSON response with status code 205.

        Raises:
            ValidationError: If the request data is invalid.
            PermissionDenied: If the user is not authenticated.
        """
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
    """

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Logs out all the user's tokens.

        Args:
            request: The HTTP request object.

        Returns:
            A JSON response with status code 205.

        Raises:
            PermissionDenied: If the user is not authenticated.
        """
        tokens = OutstandingToken.objects.filter(user_id=request.user.id)
        for token in tokens:
            t, _ = BlacklistedToken.objects.get_or_create(token=token)

        return Response(status=status.HTTP_205_RESET_CONTENT)
