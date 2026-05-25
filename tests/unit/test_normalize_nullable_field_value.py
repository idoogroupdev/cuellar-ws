import pytest
from django.core.exceptions import ValidationError

from users.models import User
from utils.functions.normalize_nullable_field_value import (
    normalize_nullable_field_value,
)


def test_normalize_nullable_field_value_returns_original_when_value_is_not_none():
    user = User()

    value = normalize_nullable_field_value(user, "last_name", "Cuellar")

    assert value == "Cuellar"


def test_normalize_nullable_field_value_returns_none_for_nullable_field():
    user = User()

    value = normalize_nullable_field_value(user, "role", None)

    assert value is None


def test_normalize_nullable_field_value_returns_empty_string_for_non_nullable_text_field():
    user = User()

    value = normalize_nullable_field_value(user, "last_name", None)

    assert value == ""


def test_normalize_nullable_field_value_raises_for_non_nullable_non_text_field():
    user = User()

    with pytest.raises(ValidationError) as exc:
        normalize_nullable_field_value(user, "is_active", None)

    assert exc.value.message_dict == {"is_active": ["This field cannot be null."]}
