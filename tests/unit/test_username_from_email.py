import pytest

from utils.functions.username_from_email import username_from_email


@pytest.mark.parametrize(
    "email,username",
    [
        ("user@example.com", "user"),
        ("USER@EXAMPLE.COM", "USER"),
        ("User234@example.COM", "User234"),
        ("usuario.nombre@example.com", "usuario.nombre"),
    ],
)
def test_username_from_email(email, username):
    assert username_from_email(email) == username
