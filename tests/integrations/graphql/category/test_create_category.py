import pytest

from roles.models import DefaultSystemRole, Role
from users.models import User

query = """
mutation MyMutation($input: CreateCategoryInput!) {
  createCategory(input:$input) {
    category {
      id
      isActive
      name
      sortOrder
    }
  }
}
"""


def build_input(**overrides):
    data = {
        "name": "Test Category",
        "sortOrder": 0,
        "isActive": True,
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_create_category_permission_denied_when_user_is_not_staff(client_query, client):
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
def test_create_category_permission_denied_when_staff_lacks_add_category_permission(
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
def test_create_category_success(client_query, client, setup_system_roles):
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

    result = client_query(query, variables={"input": build_input()}).json()

    assert result["data"]["createCategory"]["category"] == {
        "id": str(result["data"]["createCategory"]["category"]["id"]),
        "isActive": True,
        "name": "Test Category",
        "sortOrder": 0,
    }


@pytest.mark.django_db
def test_create_category_unauthorized(client_query):
    result = client_query(query, variables={"input": build_input()}).json()

    assert result["errors"][0]["extensions"] == {"code": "UNAUTHORIZED"}
