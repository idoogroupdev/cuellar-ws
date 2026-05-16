from typing import Literal, Union

from django.db.models import Model
from graphql_jwt.decorators import user_passes_test

from utils.exceptions import PermissionDenied, Unauthorized, UserNotVerified


def permission_required(
    model: Model,
    actions: Union[
        Literal["view"], Literal["add"], Literal["change"], Literal["delete"]
    ],
):
    """Check if the user has the required permissions"""

    app_label = model._meta.app_label
    model_name = model._meta.model_name

    def check_perms(user):

        if not user.is_authenticated:
            raise Unauthorized

        if not user.is_verified:
            raise UserNotVerified

        if isinstance(actions, str):
            perms = (f"{app_label}.{actions}_{model_name}",)

        else:
            perms = [f"{app_label}.{action}_{model_name}" for action in actions]

        has_perms = user.has_perms(perms)

        return has_perms

    return user_passes_test(check_perms, exc=PermissionDenied)
