import pytest

from tests.autofixture import AutoFixture
from users.models import AccountVerification

query = """
mutation verifyAuthCode ($input: VerifyAuthCodeInput!) {
  verifyAuthCode(
    input: $input
  ) {
    refreshToken
    token
    payload
    refreshExpiresIn
    user {
      email
    }
  }
}
"""


@pytest.fixture
def verification():
    return AutoFixture(
        AccountVerification, overrides={"expires_at": None, "verified_at": None}
    ).create()


@pytest.mark.django_db
def test_verify_auth_code(client_query, verification):

    result = client_query(
        query,
        variables={
            "input": {
                "email": verification.user.email,
                "code": verification.code,
                "authCode": "REGISTRATION",
            }
        },
    ).json()

    assert result["data"]["verifyAuthCode"]["user"]["email"] == verification.user.email
    assert result["data"]["verifyAuthCode"]["token"]
    assert result["data"]["verifyAuthCode"]["refreshToken"]
    assert result["data"]["verifyAuthCode"]["payload"]
    assert result["data"]["verifyAuthCode"]["refreshExpiresIn"]
