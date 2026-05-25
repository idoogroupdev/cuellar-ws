import pytest

from tests.autofixture import AutoFixture
from users.models import User

query = """
mutation updateMe($input: UpdateMeInput!) {
  updateMe(input: $input) {
    user {
      email
      firstName
      lastName
      phone
    }
  }
}
"""


@pytest.mark.django_db
def test_update_me_unauthorized(client_query):
    result = client_query(
        query,
        variables={
            "input": {
                "firstName": "New",
            }
        },
    ).json()

    assert result["errors"][0]["extensions"] == {"code": "UNAUTHORIZED"}


@pytest.mark.django_db
def test_update_me_validation_error(client_query, client):
    user = AutoFixture(User).create()
    client.force_login(user)

    result = client_query(
        query,
        variables={
            "input": {
                "phone": "123456789",
            }
        },
    ).json()

    assert result["errors"][0]["extensions"]["code"] == "VALIDATION_ERROR"
    assert "phone" in result["errors"][0]["extensions"]["fields"]


@pytest.mark.django_db
def test_update_me_success(client_query, client):
    user = AutoFixture(
        User,
        overrides={
            "first_name": "Old",
            "last_name": "Name",
            "state": User.StateChoices.NONE,
            "username": "oldname",
        },
    ).create()
    client.force_login(user)

    result = client_query(
        query,
        variables={
            "input": {
                "firstName": "New",
                "lastName": "Last",
                "phone": "+5356734300",
            }
        },
    ).json()

    user.refresh_from_db()

    assert result["data"]["updateMe"]["user"] == {
        "email": user.email,
        "firstName": "New",
        "lastName": "Last",
        "phone": "+5356734300",
    }
    assert user.first_name == "New"
    assert user.last_name == "Last"
    assert str(user.phone) == "+5356734300"
