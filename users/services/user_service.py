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

        UserService.validate_password(password)
        UserService.validate_email(email)
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
