from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from tests.autofixture import AutoFixture
from users.models import AccountVerification, User
from users.services.auth_service import AuthCodeEnum, AuthService


@pytest.fixture
def verification():
    return AutoFixture(AccountVerification).create()


@pytest.mark.django_db
def test_verify_auth_code_invalid_email():
    with pytest.raises(ValidationError):
        AuthService.verify_auth_code(
            "email.com", code="456879", auth_code=AuthCodeEnum.REGISTRATION
        )


@pytest.mark.django_db
def test_verify_auth_code_email_not_exists():
    with pytest.raises(ValueError):
        AuthService.verify_auth_code(
            "user@example.com", code="456879", auth_code=AuthCodeEnum.REGISTRATION
        )


@pytest.mark.django_db
def test_verify_auth_code_expired(verification):

    verification.expires_at = timezone.now() - timedelta(minutes=11)
    verification.save()

    with pytest.raises(ValueError, match="Auth code expired"):
        AuthService.verify_auth_code(
            verification.user.email,
            code=verification.code,
            auth_code=AuthCodeEnum.REGISTRATION,
        )


@pytest.mark.django_db
def test_verify_auth_code_already_verified(verification):

    verification.verified_at = timezone.now() - timedelta(minutes=11)
    verification.expires_at = None
    verification.save()

    with pytest.raises(ValueError, match="User is already verified"):
        AuthService.verify_auth_code(
            verification.user.email,
            code=verification.code,
            auth_code=AuthCodeEnum.REGISTRATION,
        )


@pytest.mark.django_db
def test_verify_auth_code_invalid_code(verification):

    verification.verified_at = None
    verification.expires_at = None
    verification.save()

    with pytest.raises(ValueError, match="Invalid auth code"):
        AuthService.verify_auth_code(
            verification.user.email,
            code="test",
            auth_code=AuthCodeEnum.REGISTRATION,
        )


@pytest.mark.django_db
def test_verify_auth_code(verification):

    verification.verified_at = None
    verification.expires_at = None
    verification.save()

    user, auth_info = AuthService.verify_auth_code(
        verification.user.email,
        code=verification.code,
        auth_code=AuthCodeEnum.REGISTRATION,
    )

    assert isinstance(user, User)
    assert auth_info
