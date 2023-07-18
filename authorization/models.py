from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):

    use_in_migration = True

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is Required")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff = True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser = True")

        return self.create_user(username, password, **extra_fields)


class User(AbstractUser):
    """
    A User class

    Username and password are required. Other fields are optional.
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
