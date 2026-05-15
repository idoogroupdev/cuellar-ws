from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _


class DefaultSystemRole(models.TextChoices):
    CLIENT = "CLIENT"
    SALESPERSON = "SALESPERSON"
    DELIVERY = "DELIVERY"
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"


class Role(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="role")
    name = models.CharField(
        verbose_name=_("name"), max_length=50, unique=True, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
