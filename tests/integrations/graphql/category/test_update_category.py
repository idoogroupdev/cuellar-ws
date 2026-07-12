import pytest

from branches.services.category_service import CategoryService
from roles.models import DefaultSystemRole, Role
from users.models import User

query = """
mutation MyMutation ($input: UpdateCategoryInput!) {
  updateCategory(input: $input) {
    category {
      id
      isActive
      name
      sortOrder
    }
  }
}
"""


@pytest.mark.django_db
def test_update_category_permission_denied_when_user_is_not_staff(client_query, client):
    user = User.objects.create_user(
        username="client",
        email="client@example.com",
        password="123456Dfddfe",
        is_verified=True,
    )
    client.force_login(user)

    result = client_query(
        query,
        variables={"input": {"id": str(user.id), "name": "Test Category"}},
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_update_category_permission_denied_when_staff_lacks_change_category_permission(
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
        variables={"input": {"id": str(user.id), "name": "Test Category"}},
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_update_category_success(client_query, client, setup_system_roles):
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

    category = CategoryService.create(name="Test Category")

    result = client_query(
        query,
        variables={
            "input": {
                "id": str(category.id),
                "name": "Test Category",
                "sortOrder": 0,
                "isActive": False,
            }
        },  # noqa
    ).json()

    assert result["data"]["updateCategory"]["category"] == {
        "id": str(result["data"]["updateCategory"]["category"]["id"]),
        "isActive": False,
        "name": "Test Category",
        "sortOrder": 0,
    }


@pytest.mark.django_db
def test_update_category_unauthorized(client_query):
    result = client_query(query, variables={"input": {"id": 1}}).json()

    assert result["errors"][0]["extensions"] == {"code": "UNAUTHORIZED"}
