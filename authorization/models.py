from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


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
            "Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    password = models.CharField(_("password"), max_length=128, null=False, blank=False)
    first_name = models.CharField(_("first name"), max_length=50, null=False, blank=True)
    last_name = models.CharField(_("last name"), max_length=50, blank=True)
    id = models.BigAutoField(primary_key=True, auto_created=True, db_index=True, verbose_name="user id")
    REQUIRED_FIELDS = ["password"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
