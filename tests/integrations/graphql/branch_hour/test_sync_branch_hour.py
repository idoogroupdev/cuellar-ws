import pytest

from branches.services.branch_service import BranchService
from roles.models import DefaultSystemRole, Role
from users.models import User

query = """
mutation MyMutation ($input: SyncBranchHourInput!) {
  syncBranchHour(
    input: $input
  ) {
    branchHours {
      dayOfWeek
      fromHour
      id
      toHour
    }
  }
}
"""


def build_input(**overrides):
    data = {
        "branchId": "1",
        "hours": [
            {
                "dayOfWeek": "MONDAY",
                "fromHour": "08:00",
                "toHour": "17:00",
            },
            {
                "dayOfWeek": "TUESDAY",
                "fromHour": "09:00",
                "toHour": "18:00",
            },
        ],
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_sync_branch_hour_permission_denied_when_user_is_not_staff(
    client_query, client
):
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
def test_sync_branch_hour_permission_denied_when_staff_lacks_change_branch_hour_permission(
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
def test_sync_branch_hour_success(client_query, client, setup_system_roles):
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

    branch = BranchService.create_branch(name="Test")

    result = client_query(
        query, variables={"input": build_input(branchId=branch.id)}
    ).json()

    assert result["data"]["syncBranchHour"]["branchHours"] == [
        {
            "dayOfWeek": "MONDAY",
            "fromHour": "08:00:00",
            "id": str(result["data"]["syncBranchHour"]["branchHours"][0]["id"]),
            "toHour": "17:00:00",
        },
        {
            "dayOfWeek": "TUESDAY",
            "fromHour": "09:00:00",
            "id": str(result["data"]["syncBranchHour"]["branchHours"][1]["id"]),
            "toHour": "18:00:00",
        },
    ]


@pytest.mark.django_db
def test_sync_branch_hours_unauthorized(client_query):
    result = client_query(query, variables={"input": build_input()}).json()

    assert result["errors"][0]["extensions"] == {"code": "UNAUTHORIZED"}
