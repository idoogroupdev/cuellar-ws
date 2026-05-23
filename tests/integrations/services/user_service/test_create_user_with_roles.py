import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from faker import Faker

from roles.models import DefaultSystemRole, Role
from users.services.user_service import UserService

fake = Faker()


@pytest.mark.django_db
def test_create_user_with_roles_empty_role_name():

    with pytest.raises(ValidationError):
        UserService.create_user_with_role(
            email=fake.email(),
            password=fake.password(),
            role_name="",
        )


@pytest.mark.django_db
def test_create_user_with_role_not_exists():

    with pytest.raises(ValidationError):
        UserService.create_user_with_role(
            email=fake.email(),
            password=fake.password(),
            role_name="not_existing_role",
        )

    with pytest.raises(ValidationError):
        UserService.create_user_with_role(
            email=fake.email(),
            password=fake.password(),
            role_name=DefaultSystemRole.CLIENT,
        )


@pytest.mark.django_db
def test_create_user_with_role_simple_password():

    with pytest.raises(ValidationError):
        UserService.create_user_with_role(
            email=fake.email(),
            password="123456",
            role_name=DefaultSystemRole.CLIENT,
        )


@pytest.mark.django_db
def test_create_user_with_role_invalid_email():

    with pytest.raises(ValidationError):
        UserService.create_user_with_role(
            email="invalid.email.com",
            password=fake.password(),
            role_name=DefaultSystemRole.CLIENT,
        )


@pytest.mark.django_db
def test_create_user_with_role_invalid_phone():

    with pytest.raises(ValidationError):
        UserService.create_user_with_role(
            email=fake.email(),
            password=fake.password(),
            role_name=DefaultSystemRole.CLIENT,
            phone="123456789",
        )


@pytest.mark.django_db
def test_create_user_with_roles(setup_system_roles):

    user = UserService.create_user_with_role(
        email=fake.email(),
        password=fake.password(),
        role_name=DefaultSystemRole.CLIENT,
        first_name=fake.first_name(),
        phone="+5356734300",
    )

    assert user.role == Role.objects.get(name=DefaultSystemRole.CLIENT)
    assert set(user.groups.all()) == set(
        Group.objects.filter(name__in=[DefaultSystemRole.CLIENT]).all()
    )


@pytest.mark.django_db
def test_create_user_with_roles_email_already_exists(setup_system_roles):
    email = fake.email()

    UserService.create_user_with_role(
        email=email,
        password=fake.password(),
        role_name=DefaultSystemRole.CLIENT,
    )

    with pytest.raises(ValidationError):
        UserService.create_user_with_role(
            email=email,
            password=fake.password(),
            role_name=DefaultSystemRole.CLIENT,
        )


@pytest.mark.django_db
def test_create_user_with_roles_phone_already_exists(setup_system_roles):

    UserService.create_user_with_role(
        email=fake.email(),
        password=fake.password(),
        role_name=DefaultSystemRole.CLIENT,
        phone="+5356734300",
    )

    with pytest.raises(ValidationError):
        UserService.create_user_with_role(
            email=fake.email(),
            password=fake.password(),
            role_name=DefaultSystemRole.CLIENT,
            phone="+5356734300",
        )
