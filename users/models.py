from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from roles.models import Role


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    roles = models.ManyToManyField(Role)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
