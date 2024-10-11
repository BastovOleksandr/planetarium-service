from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

from user.managers import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email_address"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return (
            f"First name: {self.first_name}\n"
            f"Last name: {self.last_name}\n"
            f"Email: {self.email}"
        )
