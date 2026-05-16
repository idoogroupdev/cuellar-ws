import pytest

query = """
mutation registerClient($input: RegisterUserInput!) {
  registerClient(input: $input) {
    user {
      email
      firstName
      id
      isActive
      isStaff
      isSuperuser
      lastName
      username
      isVerified
    }
  }
}
"""


@pytest.mark.django_db
def test_register_client_simple_password(client_query):
    result = client_query(
        query, variables={"input": {"email": "test@test.com", "password": "123456"}}
    ).json()

    assert result["errors"][0]["extensions"] == {
        "code": "VALIDATION_ERROR",
        "fields": {
            "password": [
                "This password is too short. It must contain at least 8 characters."
            ]
        },
    }


@pytest.mark.django_db
def test_register_client_invalid_email(client_query):
    result = client_query(
        query,
        variables={"input": {"email": "testtest.com", "password": "123456Dfddfe"}},
    ).json()

    assert result["errors"][0]["extensions"] == {
        "code": "VALIDATION_ERROR",
        "fields": {"email": ["Enter a valid email address."]},
    }


@pytest.mark.django_db
def test_register_client(client_query, setup_system_roles):
    result = client_query(
        query,
        variables={"input": {"email": "test@test.com", "password": "123456Dfddfe"}},
    ).json()

    assert result["data"]["registerClient"]["user"] == {
        "email": "test@test.com",
        "firstName": "",
        "id": result["data"]["registerClient"]["user"]["id"],
        "isActive": True,
        "isStaff": False,
        "isSuperuser": False,
        "lastName": "",
        "username": result["data"]["registerClient"]["user"]["username"],
        "isVerified": False,
    }
