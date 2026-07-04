import pytest

from branches.services.branch_service import BranchService
from roles.models import DefaultSystemRole, Role
from users.models import User

query = """
mutation UpdateBranch($input: UpdateBranchInput!) {
  updateBranch(input: $input) {
    branch {
      address
      id
      isActive
      isPickupEnabled
      name
    }
  }
}
"""


@pytest.mark.django_db
def test_update_branch_permission_denied_when_user_is_not_staff(client_query, client):
    user = User.objects.create_user(
        username="client",
        email="client@example.com",
        password="123456Dfddfe",
        is_verified=True,
    )
    client.force_login(user)

    result = client_query(
        query,
        variables={"input": {"id": str(user.id), "name": "Test Branch"}},
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_update_branch_permission_denied_when_staff_lacks_change_branch_permission(
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
        variables={"input": {"id": str(user.id), "name": "Test Branch"}},
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_update_branch_success(client_query, client, setup_system_roles):
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

    branch = BranchService.create_branch(name="Test Branch")

    result = client_query(
        query,
        variables={
            "input": {
                "id": str(branch.id),
                "name": "Test Branch",
                "address": "Test Address",
                "isActive": False,
                "isPickupEnabled": False,
            }
        },
    ).json()

    assert result["data"]["updateBranch"]["branch"] == {
        "address": "Test Address",
        "id": str(result["data"]["updateBranch"]["branch"]["id"]),
        "isActive": False,
        "name": "Test Branch",
        "isPickupEnabled": False,
    }


@pytest.mark.django_db
def test_update_branch_unauthorized(client_query):
    result = client_query(query, variables={"input": {"id": 1}}).json()

    assert result["errors"][0]["extensions"] == {"code": "UNAUTHORIZED"}
