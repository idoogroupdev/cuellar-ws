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
    except ValidationError as exc:
        raise ValidationError({"password": exc.messages[0]}) from exc


def validate_file_size(file: FieldFile):

    if file.size > 5 * 1024 * 1024:
        raise ValidationError(_("File size must be less than 5MB"))
