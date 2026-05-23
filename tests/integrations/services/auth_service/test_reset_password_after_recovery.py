import pytest
from django.core.exceptions import ValidationError

from tests.autofixture import AutoFixture
from users.models import User
from users.services.auth_service import AuthService


@pytest.mark.django_db
def test_reset_password_after_recovery_invalid_email():
    with pytest.raises(ValidationError):
        AuthService.reset_password_after_recovery(
            email="invalid.email", new_password="Password123*"
        )


@pytest.mark.django_db
def test_reset_password_after_recovery_invalid_password():
    user = AutoFixture(
        User, overrides={"state": User.StateChoices.WAITING_FOR_NEW_PASSWD}
    ).create()

    with pytest.raises(ValidationError):
        AuthService.reset_password_after_recovery(email=user.email, new_password="123")


@pytest.mark.django_db
def test_reset_password_after_recovery_user_not_exists():
    with pytest.raises(ValueError, match="Invalid password recovery flow"):
        AuthService.reset_password_after_recovery(
            email="notfound@example.com", new_password="Password123*"
        )


@pytest.mark.django_db
def test_reset_password_after_recovery_invalid_state():
    user = AutoFixture(User, overrides={"state": User.StateChoices.NONE}).create()

    with pytest.raises(ValueError, match="User is not allowed to reset password"):
        AuthService.reset_password_after_recovery(
            email=user.email, new_password="Password123*"
        )


@pytest.mark.django_db
def test_reset_password_after_recovery_success():
    user = AutoFixture(
        User, overrides={"state": User.StateChoices.WAITING_FOR_NEW_PASSWD}
    ).create()

    updated_user = AuthService.reset_password_after_recovery(
        email=user.email, new_password="Password123*"
    )

    updated_user.refresh_from_db()

    assert updated_user.check_password("Password123*") is True
    assert updated_user.state == User.StateChoices.NONE
