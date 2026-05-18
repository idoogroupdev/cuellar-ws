from django.core.exceptions import ValidationError
from django.core.validators import validate_email as _validate_email


def validate_email(email: str):
    try:
        _validate_email(email)
    except ValidationError as exc:
        raise ValidationError({"email": exc.message}) from exc
