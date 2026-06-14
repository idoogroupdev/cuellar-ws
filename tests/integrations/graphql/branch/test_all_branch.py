import pytest

from branches.models import Branch
from branches.services.branch_service import BranchService
from tests.integrations.graphql.user.test_all_users import create_admin_user
from users.models import User

query = """
query MyQuery {
  allBranches {
    edges {
      node {
        address
        id
        isActive
        name
      }
    }
  }
}
"""


@pytest.mark.django_db
def test_all_branches_unauthorized(client_query):
    result = client_query(query).json()

    assert result["errors"][0]["extensions"] == {"code": "UNAUTHORIZED"}


@pytest.mark.django_db
def test_all_branches_permission_denied_when_user_is_not_staff(client_query, client):
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
def test_all_branches_permission_denied_when_staff_lacks_view_user_permission(
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
def test_all_branches_success(client_query, client, setup_system_roles):
    client.force_login(create_admin_user())

    BranchService.create_branch(
        name="Test Branch",
        address="Test Address",
        is_active=True,
    )

    result = client_query(query).json()

    branches = [edge["node"] for edge in result["data"]["allBranches"]["edges"]]

    assert {
        (
            branch["name"],
            branch["address"],
            branch["isActive"],
            branch["id"],
        )
        for branch in branches
    } == {
        ("Test Branch", "Test Address", True, str(Branch.objects.first().id)),
    }
