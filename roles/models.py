from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _


class DefaultSystemRole(models.TextChoices):
    CLIENT = "CLIENT"
    SALESPERSON = "SALESPERSON"
    DELIVERY_DRIVER = "DELIVERY_DRIVER"
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"
    BRANCH_OPERATOR = "BRANCH_OPERATOR"


class Role(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, related_name="role")
    name = models.CharField(
        verbose_name=_("name"), max_length=50, unique=True, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
