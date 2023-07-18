"""
Description: This module contains the user model and user manager.

Imports:

    django.contrib.auth.base_user: This module provides the BaseUserManager class, which is used to create and manage
        user objects.
    django.contrib.auth.validators: This module provides the UnicodeUsernameValidator class, which is used to validate
        usernames.
    django.db import models: This module provides the models class, which is used to create and manage database models.
    django.contrib.auth.models: This module provides the AbstractUser class, which is a base class for user models.
    django.utils.translation import gettext_lazy as _: This module provides the gettext_lazy function, which is used to
        lazy-load translations.

Models:

    User: This model represents a user in the system.

Manager:

    UserManager: This manager is used to create and manage user objects.
"""
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):

    use_in_migration = True

    def create_user(self, username, password=None, **extra_fields):
        """
        Creates and saves a user with the given username, email and password.

        Args:
            username (str): The username of the user
            password (:obj:`str`, optional): The password of the user. Defaults to None.
            **extra_fields: Extra information fields of the user.
        Return:
            authorization.models.User: The newly created user object.
        """
        if not username:
            raise ValueError("Username is Required")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        """
        Creates and saves a superuser with the given username, email and password.

        Args:
            username (str): The username of the user
            password (str): The password of the user.
            **extra_fields: Extra information fields of the user.
        Return:
            The newly created user object.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff = True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser = True")

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    """
    A User class

    Username and password are required. Other fields are optional.

    Fields:
        username: The username of the user.
        password: The password of the user.
        first_name: The first name of the user.
        last_name: The last name of the user.
        id: The id of the user
    """

    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _("username"),
        max_length=20,
        unique=True,
        null=False,
        blank=False,
        help_text=_(
            "Required. 30 characters or fewer. "
            "Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    password = models.CharField(
        _("password"), max_length=128, null=False, blank=False
    )
    first_name = models.CharField(
        _("first name"), max_length=50, null=False, blank=True
    )
    last_name = models.CharField(
        _("last name"), max_length=50, null=False, blank=True
    )
    id = models.BigAutoField(
        primary_key=True,
        auto_created=True,
        db_index=True,
        verbose_name="user id",
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["password"]

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
