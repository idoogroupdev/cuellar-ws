# users/jwt.py
from graphql_jwt.utils import jwt_payload as _jwt_payload


def jwt_payload(user, context=None):
    """Add session_version to the payload"""

    payload = _jwt_payload(user, context)

    payload["session_version"] = user.session_version

    return payload
