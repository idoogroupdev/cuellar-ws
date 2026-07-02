from unittest.mock import Mock

import pytest
from graphql import GraphQLResolveInfo

from users.models import User
from utils.decorators import permission_required
from utils.exceptions import PermissionDenied, Unauthorized, UserNotVerified


def build_info(context):
    return GraphQLResolveInfo(
        field_name="field",
        field_nodes=[],
        return_type=Mock(),
        parent_type=Mock(),
        path=None,
        schema=Mock(),
        fragments={},
        root_value=None,
        operation=Mock(),
        variable_values={},
        context=context,
        is_awaitable=lambda value: False,
    )


@pytest.mark.django_db
def test_permission_required_allows_access_with_single_permission():
    user = Mock(is_authenticated=True)
    user.has_perms.return_value = True

    context = Mock(user=user)
    info = build_info(context)

    @permission_required(User, "view")
    def resolver(root, info):
        return "ok"

    assert resolver(None, info) == "ok"
    user.has_perms.assert_called_once_with(("users.view_user",))


@pytest.mark.django_db
def test_permission_required_raises_unauthorized_for_unauthenticated_user():
    user = Mock(is_authenticated=False)

    context = Mock(user=user)
    info = build_info(context)

    @permission_required(User, "view")
    def resolver(root, info):
        return "ok"

    with pytest.raises(Unauthorized):
        resolver(None, info)


@pytest.mark.django_db
def test_permission_required_raises_permission_denied_when_user_lacks_perms():
    user = Mock(is_authenticated=True)
    user.has_perms.return_value = False

    context = Mock(user=user)
    info = build_info(context)

    @permission_required(User, "view")
    def resolver(root, info):
        return "ok"

    with pytest.raises(PermissionDenied):
        resolver(None, info)


@pytest.mark.django_db
def test_permission_required_builds_multiple_permission_strings():
    user = Mock(is_authenticated=True)
    user.has_perms.return_value = False

    context = Mock(user=user)
    info = build_info(context)

    @permission_required(User, ["view", "change"])
    def resolver(root, info):
        return "ok"

    with pytest.raises(PermissionDenied):
        resolver(None, info)

    user.has_perms.assert_called_once_with(["users.view_user", "users.change_user"])


@pytest.mark.django_db
def test_permission_required_raises_user_not_verified():
    user = Mock(is_authenticated=True, is_verified=False)

    context = Mock(user=user)
    info = build_info(context)

    @permission_required(User, "view")
    def resolver(root, info):
        return "ok"

    with pytest.raises(UserNotVerified):
        resolver(None, info)


@pytest.mark.django_db
def test_permission_required_raises_permission_denied_when_user_has_no_role():
    user = Mock(is_authenticated=True)
    user.has_roles.return_value = False
    user.has_perms.return_value = True
    context = Mock(user=user)
    info = build_info(context)

    @permission_required(User, "view", ["ADMIN"])
    def resolver(root, info):
        return "ok"

    with pytest.raises(PermissionDenied):
        resolver(None, info)
