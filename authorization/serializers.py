from rest_framework import serializers

from .models import User


class UserRegisterSerializer(serializers.ModelSerializer):
    """
        Serializer for registering new users.

        Fields:
            id: The ID of the user.
            username: The username of the user.
            password: The password of the user.
            first_name: The first name of the user.
            last_name: The last name of the user.

    """
    class Meta:
        model = User
        fields = ["id", "username", "password", "first_name", "last_name"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """
            Create a new user and save it to the database.

            Args:
                validated_data (dict): The data that was validated by the serializer.

            Returns:
                authorization.models.User: The newly created user object.
        """
        print(type(validated_data))
        user = User.objects.create(
            **validated_data
        )
        user.set_password(validated_data['password'])
        user.save()
        print(type(user))
        return user


class UserSerializer(serializers.ModelSerializer):
    """
        Serializer for retrieving and updating user information.

        Fields:
            id: The ID of the user.
            username: The username of the user.
            first_name: The first name of the user.
            last_name: The last name of the user.

    """
    class Meta:
        model = User
        exclude = ['password', ]
