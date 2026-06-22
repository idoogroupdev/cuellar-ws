import secrets
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import validate_image_file_extension
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from branches.models import Branch
from roles.models import DefaultSystemRole, Role
from utils.functions.generate_unique_code import generate_unique_code
from utils.validators import validate_file_size


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


class CashbackHistory(models.Model):
    class TypeChoices(models.TextChoices):
        EARNED = "EARNED", _("Earned")
        SPENT = "SPENT", _("Spent")
        RESERVED = "RESERVED", _("Reserved")
        RELEASED = "RELEASED", _("Released")

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cashback_history"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=8, choices=TypeChoices.choices)
    balance_after = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    released_with = models.OneToOneField(
        "self", on_delete=models.PROTECT, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="check_cashback_history_amount_gt_zero",
            ),
            models.CheckConstraint(
                condition=Q(released_with__isnull=True) | Q(type="RESERVED"),
                name="released_with_only_for_reserved_type",
            ),
        ]

    def clean(self):
        if self.released_with:
            if self.type != self.TypeChoices.RESERVED:
                raise ValidationError(
                    {"released_with": _("Cannot be used with a non-reserved type")}
                )

            if self.released_with.type != self.TypeChoices.RELEASED:
                raise ValidationError(
                    {"released_with": _("Cannot be used with a non-released type")}
                )
