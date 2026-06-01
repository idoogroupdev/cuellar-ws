import pytest

from roles.models import DefaultSystemRole, Role
from users.models import User

query = """
mutation createUser($input: CreateUserInput!) {
  createUser(input: $input) {
    user {
      email
      firstName
      id
      isStaff
      isVerified
      lastName
      role {
        name
      }
      phone
    }
  }
}
"""


def build_input(**overrides):
    data = {
        "email": "user@example.com",
        "password": "123456Dfddfe*",
        "roleName": DefaultSystemRole.SALESPERSON.value,
        "firstName": "User",
        "lastName": "User",
        "phone": "+5356734300",
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_create_user_unauthorized(client_query):
    result = client_query(query, variables={"input": build_input()}).json()

    assert result["errors"][0]["extensions"] == {"code": "UNAUTHORIZED"}


@pytest.mark.django_db
def test_create_user_permission_denied_when_user_is_not_staff(client_query, client):
    user = User.objects.create_user(
        username="client",
        email="client@example.com",
        password="123456Dfddfe",
        is_verified=True,
    )
    client.force_login(user)

    result = client_query(query, variables={"input": build_input()}).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_create_user_permission_denied_when_staff_lacks_add_user_permission(
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

    result = client_query(query, variables={"input": build_input()}).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_create_user_with_non_staff_role_success(
    client_query, client, setup_system_roles
):
    admin_role = Role.objects.get(name=DefaultSystemRole.ADMIN)
    user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="123456Dfddfe*",
        is_staff=True,
        is_verified=True,
        role=admin_role,
    )
    user.groups.set([admin_role.group])

    client.force_login(user)

    result = client_query(
        query,
        variables={
            "input": build_input(
                lastName=None,
                roleName=DefaultSystemRole.SALESPERSON.value,
            )
        },
    ).json()

    created_user = User.objects.get(email="user@example.com")

    assert result["data"]["createUser"]["user"] == {
        "email": "user@example.com",
        "firstName": "User",
        "id": str(created_user.id),
        "isStaff": False,
        "isVerified": True,
        "lastName": "",
        "role": {"name": DefaultSystemRole.SALESPERSON.value},
        "phone": "+5356734300",
    }
    assert created_user.is_staff is False
    assert created_user.is_verified is True
    assert created_user.last_name == ""


@pytest.mark.django_db
def test_create_user_with_staff_role_success(client_query, client, setup_system_roles):
    admin_role = Role.objects.get(name=DefaultSystemRole.ADMIN)
    user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="123456Dfddfe*",
        is_staff=True,
        is_verified=True,
        role=admin_role,
    )
    user.groups.set([admin_role.group])

    client.force_login(user)

    result = client_query(
        query,
        variables={
            "input": build_input(
                email="admin-user@example.com",
                roleName=DefaultSystemRole.ADMIN.value,
            )
        },
    ).json()

    created_user = User.objects.get(email="admin-user@example.com")

    assert result["data"]["createUser"]["user"]["isStaff"] is True
    assert created_user.is_staff is True
