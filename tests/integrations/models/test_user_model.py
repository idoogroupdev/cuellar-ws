import pytest

from roles.models import DefaultSystemRole, Role
from users.models import User


@pytest.mark.django_db
def test_has_roles(setup_system_roles):
    role = Role.objects.filter(name=DefaultSystemRole.BRANCH_OPERATOR).first()

    user = User.objects.create_user(
        username="test@example.com",
        password="test",
        is_verified=True,
        role=role,
    )

    assert user.has_roles([DefaultSystemRole.BRANCH_OPERATOR]) is True
    assert user.has_roles(["BRANCH_OPERATOR"]) is True
    assert (
        user.has_roles([DefaultSystemRole.BRANCH_OPERATOR, DefaultSystemRole.CLIENT])
        is True
    )
    assert user.has_roles([DefaultSystemRole.CLIENT, DefaultSystemRole.ADMIN]) is False
