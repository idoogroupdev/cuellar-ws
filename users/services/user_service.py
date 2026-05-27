from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from roles.models import DefaultSystemRole, Role
from users.models import User
from utils.functions.generate_unique_username import generate_unique_username
from utils.functions.normalize_nullable_field_value import (
    normalize_nullable_field_value,
)
from utils.validators import validate_email, validate_password


class UserService:
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

        user = User(username=username, email=email, role=role)
        for field, value in extra_fields.items():
            setattr(user, field, normalize_nullable_field_value(user, field, value))

        user.set_password(password)
        user.full_clean()
        user.save()

        user.groups.set([role.group])

        return user

    @staticmethod
    @transaction.atomic
    def update_user(
        user: User,
        *,
        role_name: str | DefaultSystemRole | None = None,
        password: str | None = None,
        **extra_fields,
    ) -> User:
        update_fields: list[str] = []
        role_updated = False

        if role_name is not None:
            role = UserService.validate_role_name(role_name)
            if user.role_id != role.id:
                user.role = role
                update_fields.append("role")
                role_updated = True

        email = extra_fields.get("email")
        if email is not None:
            validate_email(email)

        if password:
            validate_password(password)
            user.set_password(password)
            update_fields.append("password")

        for field, value in extra_fields.items():
            value = normalize_nullable_field_value(user, field, value)

            if getattr(user, field) != value:
                setattr(user, field, value)
                update_fields.append(field)

        if update_fields:
            excluded_fields = [
                field.name
                for field in user._meta.fields
                if field.name not in update_fields
            ]
            user.full_clean(exclude=excluded_fields)
            user.save(update_fields=update_fields)

        if role_updated:
            user.groups.set([user.role.group])

        return user
