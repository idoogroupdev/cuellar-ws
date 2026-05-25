import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import validate_image_file_extension
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from roles.models import Role
from utils.functions.generate_unique_code import generate_unique_code


def client_profile_image_directory_path(instance, filename):
    token = secrets.token_urlsafe(10)
    return f"profile_images/clients/{instance.id}/{token}_{filename}"


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
        upload_to=client_profile_image_directory_path,
        validators=[validate_image_file_extension],
        blank=True,
        null=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


def default_expiration_date():
    return timezone.now() + timedelta(minutes=10)


class AccountVerification(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="verification"
    )
    code = models.CharField(max_length=6, null=True, blank=True, db_index=True)
    expires_at = models.DateTimeField(
        default=default_expiration_date, null=True, blank=True
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.expires_at is not None and self.expires_at < timezone.now()

    def is_verified(self):
        return self.verified_at is not None

    def mark_as_verified(self):
        self.user.is_verified = True
        self.user.save(update_fields=["is_verified"])

        self.verified_at = timezone.now()
        self.code = None
        self.save(update_fields=["verified_at", "code"])

    def generate_code(self):
        self.code = generate_unique_code(self.__class__)
        self.expires_at = default_expiration_date()
        self.save(update_fields=["code", "expires_at"])

    def is_valid_code(self, code: str):
        return self.code == code


class RecoverPassword(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="recover_password"
    )
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiration_date)

    def generate_code(self):
        self.code = generate_unique_code(self.__class__)
        self.expires_at = default_expiration_date()
        self.save(update_fields=["code", "expires_at"])

    def is_expired(self):
        return self.expires_at is not None and self.expires_at < timezone.now()

    def is_valid_code(self, code: str):
        return self.code == code
