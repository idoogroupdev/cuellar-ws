import secrets

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from branches.models import Branch
from roles.models import DefaultSystemRole, Role
from utils.validators import validate_file_size


def user_profile_image_directory_path(instance, filename):
    token = secrets.token_urlsafe(10)
    return f"profile_images/users/{instance.id}/{token}_{filename}"


class User(AbstractUser):
    class StateChoices(models.TextChoices):
        NONE = "NONE", _("None")
        WAITING_FOR_NEW_PASSWD = (
            "WAITING_FOR_NEW_PASSWD",
            _("Waiting for new password"),
        )

    email = models.EmailField(_("email address"), unique=True)
    role = models.ForeignKey(
        Role, on_delete=models.SET_NULL, related_name="users", null=True, blank=True
    )
    is_verified = models.BooleanField(default=False)
    state = models.CharField(
        max_length=22,
        choices=StateChoices.choices,
        default=StateChoices.NONE,
        null=True,
        blank=True,
    )
    phone = PhoneNumberField(
        verbose_name=_("phone"), blank=True, null=True, unique=True
    )
    profile_image = models.ImageField(
        upload_to=user_profile_image_directory_path,
        validators=[validate_image_file_extension, validate_file_size],
        blank=True,
        null=True,
    )
    session_version = models.PositiveIntegerField(default=1)
    branch = models.ForeignKey(
        Branch,
        on_delete=models.SET_NULL,
        related_name="users",
        null=True,
        blank=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(is_superuser=False) | Q(is_active=True),
                name="superuser_must_be_active",
            ),
        ]

    def clean(self):
        if self.is_superuser and not self.is_active:
            raise ValidationError(
                {"is_active": _("A superuser cannot be deactivated.")}
            )

        if self.role and self.role.name == DefaultSystemRole.CLIENT and not self.phone:
            raise ValidationError({"phone": _("A client must have a phone number.")})
