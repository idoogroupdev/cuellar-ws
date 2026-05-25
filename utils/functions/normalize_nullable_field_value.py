from django.core.exceptions import ValidationError
from django.db.models import Model
from django.utils.translation import gettext_lazy as _


def normalize_nullable_field_value(instance: Model, field: str, value):
    model_field = instance._meta.get_field(field)
    if value is not None or model_field.null:
        return value

    if getattr(model_field, "empty_strings_allowed", False):
        return ""

    raise ValidationError({field: _("This field cannot be null.")})
