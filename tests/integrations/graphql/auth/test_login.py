import pytest
from fcm_django.models import FCMDevice

from roles.models import DefaultSystemRole, Role
from users.models import User

query = """
mutation MyMutation (
    $email: String!
    $password: String!
    $deviceType: DeviceType
    $deviceId: String
    $firebaseRegistrationId: String
    $isMobile: Boolean
  )
    {
  login(
    email: $email
    password: $password
    deviceType: $deviceType
    deviceId: $deviceId
    firebaseRegistrationId: $firebaseRegistrationId
    isMobile: $isMobile
  ) {
    payload
    refreshExpiresIn
    refreshToken
    token
    user {
      email
    }
  }
}
"""


@pytest.mark.django_db
def test_login_success(client_query, setup_system_roles):
    client_role = Role.objects.get(name=DefaultSystemRole.CLIENT)
    user = User.objects.create_user(
        username="client",
        email="client@example.com",
        password="123456Dfddfe*",
        is_verified=True,
        role=client_role,
    )
    user.groups.set([client_role.group])

    result = client_query(
        query,
        variables={
            "email": "client@example.com",
            "password": "123456Dfddfe*",
            "deviceType": "ANDROID",
            "deviceId": "123456",
            "firebaseRegistrationId": "123456",
            "isMobile": True,
        },
    ).json()

    assert result["data"]["login"]["user"]["email"] == "client@example.com"

    device = FCMDevice.objects.get(registration_id="123456")
    assert device.user_id == user.id


@pytest.mark.django_db
def test_login_role_admin_from_mobile(client_query, setup_system_roles):
    admin_role = Role.objects.get(name=DefaultSystemRole.ADMIN)
    user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="123456Dfddfe*",
        is_verified=True,
        role=admin_role,
    )
    user.groups.set([admin_role.group])

    result = client_query(
        query,
        variables={
            "email": "admin@example.com",
            "password": "123456Dfddfe*",
            "deviceType": "ANDROID",
            "deviceId": "123456",
            "firebaseRegistrationId": "123456",
            "isMobile": True,
        },
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "PERMISSION_DENIED"}


@pytest.mark.django_db
def test_check_only_one_session_active(client_query):
    User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="123456Dfddfe*",
        is_verified=True,
    )

    result = client_query(
        query,
        variables={
            "email": "admin@example.com",
            "password": "123456Dfddfe*",
        },
    ).json()

    session1 = result["data"]["login"]["token"]

    result = client_query(
        query,
        variables={
            "email": "admin@example.com",
            "password": "123456Dfddfe*",
        },
    ).json()

    session2 = result["data"]["login"]["token"]

    query_me = """
    query MyQuery {
    me {
        email
    }
    }
    """

    result1 = client_query(
        query_me, headers={"Authorization": f"JWT {session1}"}
    ).json()

    assert result1["errors"][0]["message"] == "Your session has been closed."

    result2 = client_query(
        query_me, headers={"Authorization": f"JWT {session2}"}
    ).json()

    assert result2["data"]["me"]["email"] == "admin@example.com"
