import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from faker import Faker

from roles.models import DefaultSystemRole, Role
from users.services.user_service import UserService

fake = Faker()


@pytest.mark.django_db
def test_create_user_with_roles_empty_role_names():

    with pytest.raises(ValueError):
        UserService.create_user_with_roles(
            email=fake.email(),
            password=fake.password(),
            role_names=[],
        )


@pytest.mark.django_db
def test_create_user_with_roles_role_not_exists(setup_system_roles):

    with pytest.raises(ValueError, match="Roles not found: not_existing_role"):
        UserService.create_user_with_roles(
            email=fake.email(),
            password=fake.password(),
            role_names=["not_existing_role", DefaultSystemRole.CLIENT],
        )


@pytest.mark.django_db
def test_create_user_with_roles_simple_password():

    with pytest.raises(ValidationError):
        UserService.create_user_with_roles(
            email=fake.email(),
            password="123456",
            role_names=[DefaultSystemRole.CLIENT],
        )


@pytest.mark.django_db
def test_create_user_with_roles_invalid_email():

    with pytest.raises(ValidationError):
        UserService.create_user_with_roles(
            email="invalid.email.com",
            password=fake.password(),
            role_names=[DefaultSystemRole.CLIENT],
        )


@pytest.mark.django_db
def test_create_user_with_roles(setup_system_roles):

    role_names = [DefaultSystemRole.CLIENT, DefaultSystemRole.ADMIN]

    user = UserService.create_user_with_roles(
        email=fake.email(),
        password=fake.password(),
        role_names=role_names,
    )

    assert set(user.roles.all()) == set(Role.objects.filter(name__in=role_names).all())
    assert set(user.groups.all()) == set(
        Group.objects.filter(name__in=role_names).all()
    )
