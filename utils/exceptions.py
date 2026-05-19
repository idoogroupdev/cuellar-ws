from django.utils.translation import gettext_lazy as _
from graphql.error import GraphQLError


class PermissionDenied(GraphQLError):
    """
    Raised when user is logged in but does not have permission
    """

    message = _("You do not have permission to perform this action.")

    def __init__(self, message=None):
        super().__init__(
            message or self.message, extensions={"code": "PERMISSION_DENIED"}
        )


class Unauthorized(GraphQLError):
    """
    Raised when user is not logged in
    or token is invalid
    """

    message = _("You are not authorized to perform this action.")

    def __init__(self, message=None):
        super().__init__(self.message, extensions={"code": "UNAUTHORIZED"})


class UserNotVerified(GraphQLError):
    """
    Raised when user is not verified
    """

    message = _("Your account is not verified.")

    def __init__(self, message=None):
        super().__init__(self.message, extensions={"code": "USER_NOT_VERIFIED"})


class ValidationGraphQLError(GraphQLError):
    message = _("Validation error")

    def __init__(
        self,
        fields: dict,
    ):
        super().__init__(
            self.message,
            extensions={
                "code": "VALIDATION_ERROR",
                "fields": fields,
            },
        )


class TooManyAttempts(GraphQLError):
    message = _("Too many attempts. Try again in %(count)s seconds.")

    def __init__(self, seconds: int, message=None):
        _message = message or self.message

        super().__init__(
            _message % {"count": seconds},
            extensions={"code": "TOO_MANY_ATTEMPTS", "seconds": seconds},
        )
