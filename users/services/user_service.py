from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from roles.models import DefaultSystemRole, Role
from users.models import User
from utils.functions.generate_unique_username import generate_unique_username


class UserService:
    @staticmethod
    @transaction.atomic
    def create_user_with_roles(
        *,
        email: str,
        password: str,
        role_names: list[str | DefaultSystemRole],
        **extra_fields,
    ) -> User:

        validate_password(password)
        validate_email(email)

        if not role_names:
            raise ValueError(_("At least one role is required"))

        normalized_role_names = [
            role.value if isinstance(role, DefaultSystemRole) else role
            for role in role_names
        ]
        unique_role_names = list(set(normalized_role_names))

        roles = list(Role.objects.filter(name__in=unique_role_names))

        found_role_names = {role.name for role in roles}
        missing_roles = list(set(unique_role_names) - found_role_names)

        if missing_roles:
            raise ValueError(
                _("Roles not found: %(roles)s") % {"roles": ", ".join(missing_roles)}
            )

        username = generate_unique_username(email)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            **extra_fields,
        )

        user.roles.set(roles)
        user.groups.set([role.group for role in roles])

        return user
