from django.contrib.auth.password_validation import (
    validate_password as _validate_password,
)
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as _validate_email


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
