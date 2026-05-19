import pytest
from django.core.exceptions import ValidationError

from tests.autofixture import AutoFixture
from users.models import User
from users.services.auth_service import AuthCodeEnum, AuthService


@pytest.mark.django_db
def test_send_auth_code_invalid_email():
    with pytest.raises(ValidationError):
        AuthService.send_auth_code(
            email="invalid.email.com", auth_code=AuthCodeEnum.REGISTRATION
        )


@pytest.mark.django_db
def test_send_auth_code_user_not_exists():
    with pytest.raises(
        ValueError, match="You cannot request a auth code for this time"
    ):
        AuthService.send_auth_code(
            email="user@email.com", auth_code=AuthCodeEnum.REGISTRATION
        )


@pytest.mark.django_db
def test_send_auth_code_user_verified():
    user = AutoFixture(User, overrides={"is_verified": True}).create()

    with pytest.raises(ValueError, match="User is already verified"):
        AuthService.send_auth_code(
            email=user.email, auth_code=AuthCodeEnum.REGISTRATION
        )
