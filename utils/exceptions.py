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
