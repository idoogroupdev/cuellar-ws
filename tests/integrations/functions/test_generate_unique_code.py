import pytest

from users.models import AccountVerification
from utils.functions.generate_unique_code import generate_unique_code


@pytest.mark.django_db
def test_generate_unique_code():
    code = generate_unique_code(AccountVerification, is_alphanumeric=False)
    assert len(code) == 6
    assert code.isdigit()


@pytest.mark.django_db
def test_generate_unique_code_alphanumeric():
    code = generate_unique_code(AccountVerification, is_alphanumeric=True)
    assert len(code) == 6
    assert code.isalnum()


@pytest.mark.django_db
def test_generate_unique_code_field_not_found():
    with pytest.raises(ValueError):
        generate_unique_code(AccountVerification, field_name="not_found")
