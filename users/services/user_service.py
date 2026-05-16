from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from roles.models import DefaultSystemRole, Role
from users.models import User
from utils.functions.generate_unique_username import generate_unique_username


class UserService:
    @staticmethod
    def validate_password(password: str):
        try:
            validate_password(password)
        except ValidationError as exc:
            raise ValidationError({"password": exc.messages[0]}) from exc

    @staticmethod
    def validate_email(email: str):
        try:
            validate_email(email)
        except ValidationError as exc:
            raise ValidationError({"email": exc.message}) from exc

    @staticmethod
    def validate_role_names(role_names: list[str | DefaultSystemRole]):
        """Validate role names and return a list of roles"""

        if not role_names:
            raise ValidationError({"role_names": _("At least one role is required")})

        normalized_role_names = [
            role.value if isinstance(role, DefaultSystemRole) else role
            for role in role_names
        ]
        unique_role_names = list(set(normalized_role_names))

        roles = list(Role.objects.filter(name__in=unique_role_names))

        found_role_names = {role.name for role in roles}
        missing_roles = list(set(unique_role_names) - found_role_names)

        if missing_roles:
            raise ValidationError(
                {
                    "role_names": _("Roles not found: %(roles)s")
                    % {"roles": ", ".join(missing_roles)}
                }
            )

        return roles

    @staticmethod
    @transaction.atomic
    def create_user_with_roles(
        *,
        email: str,
        password: str,
        role_names: list[str | DefaultSystemRole],
        **extra_fields,
    ) -> User:

        UserService.validate_password(password)
        UserService.validate_email(email)
        roles = UserService.validate_role_names(role_names)

        username = generate_unique_username(email)

        user = User(
            username=username,
            email=email,
            **extra_fields,
        )
        user.set_password(password)
        user.full_clean()
        user.save()

        user.roles.set(roles)
        user.groups.set([role.group for role in roles])

        return user
