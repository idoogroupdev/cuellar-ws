import pytest

from roles.models import DefaultSystemRole, Role
from users.models import User

query = """
mutation updateUser($input: UpdateUserInput!) {
  updateUser(input: $input) {
    user {
      email
      firstName
      id
      isStaff
      role {
        name
      }
    }
  }
}
"""


def create_admin_user():
    admin_role = Role.objects.get(name=DefaultSystemRole.ADMIN)
    user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="123456Dfddfe",
        is_staff=True,
        is_verified=True,
        role=admin_role,
    )
    user.groups.set([admin_role.group])
    return user


@pytest.mark.django_db
def test_update_user_unauthorized(client_query):
    result = client_query(
        query,
        variables={"input": {"id": "1", "firstName": "Juan"}},
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "UNAUTHORIZED"}


@pytest.mark.django_db
def test_update_user_permission_denied_when_user_is_not_staff(client_query, client):
    user = User.objects.create_user(
        username="client",
        email="client@example.com",
        password="123456Dfddfe",
        is_verified=True,
    )
    client.force_login(user)

    result = client_query(
        query,
        variables={"input": {"id": str(user.id), "firstName": "Juan"}},
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_update_user_permission_denied_when_staff_lacks_change_user_permission(
    client_query, client
):
    user = User.objects.create_user(
        username="staff_without_permission",
        email="staff-without-permission@example.com",
        password="123456Dfddfe",
        is_staff=True,
        is_verified=True,
    )
    client.force_login(user)

    result = client_query(
        query,
        variables={"input": {"id": str(user.id), "firstName": "Juan"}},
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_update_user_sets_staff_false_for_non_staff_role(
    client_query, client, setup_system_roles
):
    client_role = Role.objects.get(name=DefaultSystemRole.CLIENT)
    user = User.objects.create_user(
        username="target",
        email="target@example.com",
        password="123456Dfddfe",
        is_staff=True,
        is_verified=True,
        role=client_role,
    )
    client.force_login(create_admin_user())

    result = client_query(
        query,
        variables={"input": {"id": str(user.id), "firstName": "Juan"}},
    ).json()

    user.refresh_from_db()

    assert result["data"]["updateUser"]["user"]["firstName"] == "Juan"
    assert result["data"]["updateUser"]["user"]["isStaff"] is False
    assert user.is_staff is False


@pytest.mark.django_db
def test_update_user_sets_staff_true_for_staff_role(
    client_query, client, setup_system_roles
):
    client_role = Role.objects.get(name=DefaultSystemRole.CLIENT)
    user = User.objects.create_user(
        username="target",
        email="target@example.com",
        password="123456Dfddfe",
        is_staff=False,
        is_verified=True,
        role=client_role,
    )
    client.force_login(create_admin_user())

    result = client_query(
        query,
        variables={
            "input": {
                "id": str(user.id),
                "roleName": DefaultSystemRole.ADMIN.value,
            }
        },
    ).json()

    user.refresh_from_db()

    assert result["data"]["updateUser"]["user"]["isStaff"] is True
    assert result["data"]["updateUser"]["user"]["role"] == {
        "name": DefaultSystemRole.ADMIN.value
    }
    assert user.is_staff is True
