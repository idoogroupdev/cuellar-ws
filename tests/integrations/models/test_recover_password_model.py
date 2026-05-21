import pytest

from tests.autofixture import AutoFixture
from users.models import RecoverPassword, User


@pytest.fixture
def user():
    return AutoFixture(User).create()


@pytest.mark.django_db
def test_generate_code(user):
    verification = RecoverPassword.objects.create(user=user)
    verification.generate_code()

    assert verification.code is not None
    assert verification.expires_at is not None
