from typing import Literal, Union

from django.db.models import Model
from graphql_jwt.decorators import user_passes_test

from roles.models import DefaultSystemRoleLiteral
from utils.exceptions import PermissionDenied, Unauthorized, UserNotVerified


def permission_required(
    model: Model,
    actions: Union[
        Literal["view"], Literal["add"], Literal["change"], Literal["delete"]
    ],
    roles: Union[DefaultSystemRoleLiteral] = None,
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

        has_roles = user.has_roles(roles) if roles else True

        return has_perms and has_roles

    return user_passes_test(check_perms, exc=PermissionDenied)


login_required = user_passes_test(lambda u: u.is_authenticated, exc=Unauthorized)


def is_staff(user):
    if not user.is_authenticated:
        raise Unauthorized

    return user.is_staff


staff_member_required = user_passes_test(is_staff, exc=PermissionDenied)
