import pytest

from tests.autofixture import AutoFixture
from users.models import AccountVerification, User


@pytest.fixture
def user():
    return AutoFixture(User).create()


@pytest.mark.django_db
def test_mark_as_verified(user):
    verification = AccountVerification.objects.create(user=user)
    verification.mark_as_verified()

    assert verification.is_verified()
    assert user.is_verified


@pytest.mark.django_db
def test_generate_code(user):
    verification = AccountVerification.objects.create(user=user)
    verification.generate_code()

    assert verification.code is not None
    assert verification.expires_at is not None
