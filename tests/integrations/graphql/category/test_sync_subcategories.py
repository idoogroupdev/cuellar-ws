import pytest

from branches.models import Category
from branches.services.category_service import CategoryService
from roles.models import DefaultSystemRole, Role
from users.models import User

query = """
mutation MyMutation ($input: SyncSubcategoriesInput!) {
  syncSubcategories(input: $input) {
    success
  }
}
"""


@pytest.mark.django_db
def test_sync_subcategories_permission_denied_when_user_is_not_staff(
    client_query, client
):
    user = User.objects.create_user(
        username="client",
        email="client@example.com",
        password="123456Dfddfe",
        is_verified=True,
    )
    client.force_login(user)

    result = client_query(
        query,
        variables={"input": {"parentId": str(user.id), "names": ["Test Category"]}},
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_sync_subcategories_permission_denied_when_staff_lacks_change_category_permission(
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
        variables={"input": {"parentId": str(user.id), "names": ["Test Category"]}},
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_sync_subcategories_success(client_query, client, setup_system_roles):
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

    parent = CategoryService.create(name="Parent")
    CategoryService.create(name="Candy", parent=parent)
    CategoryService.create(name="Cookies", parent=parent)

    result = client_query(
        query,
        variables={
            "input": {
                "parentId": str(parent.id),
                "names": ["Candy", "Cookies", "Chocolate"],
            }
        },  # noqa
    ).json()

    assert result["data"]["syncSubcategories"]["success"]
    assert list(
        Category.objects.filter(parent=parent).values_list("name", "sort_order")
    ) == [
        ("Candy", 0),
        ("Cookies", 1),
        ("Chocolate", 2),
    ]


@pytest.mark.django_db
def test_sync_subcategories_unauthorized(client_query):
    result = client_query(
        query, variables={"input": {"parentId": 1, "names": []}}
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "UNAUTHORIZED"}
