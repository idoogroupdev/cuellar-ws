from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from roles.models import DefaultSystemRole, Role
from users.models import User
from utils.functions.generate_unique_username import generate_unique_username
from utils.validators import validate_email, validate_password


class UserService:
    _slots_ = [
        "validate_role_name",
        "create_user_with_role",
    ]

    @staticmethod
    def validate_role_name(role_name: str | DefaultSystemRole):
        """Validate role name and return a role"""

        if not role_name:
            raise ValidationError({"role_name": _("Role name is required")})

        role = Role.objects.filter(name=role_name).first()

        if not role:
            raise ValidationError(
                {"role_name": _("Role not found: %(role)s") % {"role": role_name}}
            )

        return role

    @staticmethod
    @transaction.atomic
    def create_user_with_role(
        *,
        email: str,
        password: str,
        role_name: str | DefaultSystemRole,
        **extra_fields,
    ) -> User:

        validate_password(password)
        validate_email(email)
        role = UserService.validate_role_name(role_name)

        username = generate_unique_username(email)

        user = User(
            username=username,
            email=email,
            role=role,
            **extra_fields,
        )
        user.set_password(password)
        user.full_clean()
        user.save()

        user.groups.set([role.group])

        return user
