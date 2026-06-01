import re

from django.contrib.auth.password_validation import (
    validate_password as _validate_password,
)
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as _validate_email
from django.db.models.fields.files import FieldFile
from django.utils.translation import gettext_lazy as _


def validate_email(email: str):
    try:
        _validate_email(email)
    except ValidationError as exc:
        raise ValidationError({"email": exc.message}) from exc


def validate_password(password: str):
    try:
        _validate_password(password)
        custom_validate_password(password)
    except ValidationError as exc:
        raise ValidationError({"password": exc.messages[0]}) from exc


def custom_validate_password(password: str):
    """
    Validates that the password meets certain requirements.
    Raises ValidationError if any requirement is not met.
    """
    errors = []

    if len(password) < 8:
        errors.append(_("Password must be at least 8 characters long."))

    if not re.search(r"[A-Z]", password):
        errors.append(_("Password must contain at least one uppercase letter."))

    if not re.search(r"[a-z]", password):
        errors.append(_("Password must contain at least one lowercase letter."))

    if not re.search(r"\d", password):
        errors.append(_("Password must contain at least one number."))

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append(_("Password must contain at least one special character."))

    if errors:
        raise ValidationError(errors)

    return True


def validate_file_size(file: FieldFile):

    if file.size > 5 * 1024 * 1024:
        raise ValidationError(_("File size must be less than 5MB"))
