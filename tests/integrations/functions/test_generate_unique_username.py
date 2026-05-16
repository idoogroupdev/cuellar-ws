import pytest

from utils.functions.generate_unique_username import generate_unique_username


@pytest.mark.django_db
def test_generate_unique_username():
    email = "user.test@example.com"
    username = generate_unique_username(email)
    assert "user.test" in username
