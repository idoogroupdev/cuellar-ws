import pytest

from roles.models import DefaultSystemRole, Role
from users.models import User
from users.services.user_service import UserService

query = """
query allUsers {
  allUsers {
    edges {
      node {
        email
        firstName
        isStaff
        role {
          name
        }
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
def test_all_users_unauthorized(client_query):
    result = client_query(query).json()

    assert result["errors"][0]["extensions"] == {"code": "UNAUTHORIZED"}


@pytest.mark.django_db
def test_all_users_permission_denied_when_user_is_not_staff(client_query, client):
    user = User.objects.create_user(
        username="client",
        email="client@example.com",
        password="123456Dfddfe",
        is_verified=True,
    )
    client.force_login(user)

    result = client_query(query).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_all_users_permission_denied_when_staff_lacks_view_user_permission(
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

    result = client_query(query).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_all_users_success(client_query, client, setup_system_roles):
    client.force_login(create_admin_user())

    UserService.create_user(
        email="client@example.com",
        password="123456Dfddfe*",
        role_name=DefaultSystemRole.CLIENT,
        first_name="Client",
        phone="+5356989898",
    )

    UserService.create_user(
        email="operator@example.com",
        password="123456Dfddfe*",
        role_name=DefaultSystemRole.OPERATOR,
        first_name="Operator",
    )

    result = client_query(query).json()

    users = [edge["node"] for edge in result["data"]["allUsers"]["edges"]]

    assert {
        (user["email"], user["firstName"], user["isStaff"], user["role"]["name"])
        for user in users
    } == {
        ("admin@example.com", "", True, DefaultSystemRole.ADMIN.value),
        ("client@example.com", "Client", False, DefaultSystemRole.CLIENT.value),
        ("operator@example.com", "Operator", True, DefaultSystemRole.OPERATOR.value),
    }
