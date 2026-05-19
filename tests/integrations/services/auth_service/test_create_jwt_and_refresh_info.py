import pytest

from tests.autofixture import AutoFixture
from users.models import User
from users.services.auth_service import AuthService


@pytest.fixture
def user():
    return AutoFixture(User).create()


@pytest.mark.django_db
def test_create_jwt_and_refresh_info(user):
    result = AuthService.create_jwt_and_refresh_info(user)

    assert result.token
    assert result.refresh_token
    assert result.refresh_expires_in
    assert result.payload
