import pytest

from tests.autofixture import AutoFixture
from users.models import User

query = """
mutation resetPassword($input: ResetPasswordInput!) {
  resetPassword(input: $input) {
    user {
      email
    }
  }
}
"""


@pytest.mark.django_db
def test_reset_password_unauthorized(client_query):
    result = client_query(
        query,
        variables={
            "input": {
                "newPassword": "Password123*",
            }
        },
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "UNAUTHORIZED"}


@pytest.mark.django_db
def test_reset_password_validation_error(client_query, client):
    user = AutoFixture(
        User,
        overrides={"state": User.StateChoices.WAITING_FOR_NEW_PASSWD},
    ).create()

    client.force_login(user)

    result = client_query(
        query,
        variables={
            "input": {
                "newPassword": "123",
            }
        },
    ).json()

    assert result["errors"][0]["extensions"]["code"] == "VALIDATION_ERROR"
    assert "password" in result["errors"][0]["extensions"]["fields"]


@pytest.mark.django_db
def test_reset_password_success(client_query, client):
    user = AutoFixture(
        User,
        overrides={"state": User.StateChoices.WAITING_FOR_NEW_PASSWD},
    ).create()

    client.force_login(user)

    new_password = "Password123*"

    result = client_query(
        query,
        variables={
            "input": {
                "newPassword": new_password,
            }
        },
    ).json()

    user.refresh_from_db()

    assert result["data"]["resetPassword"]["user"]["email"] == user.email
    assert user.check_password(new_password) is True
    assert user.state == User.StateChoices.NONE
