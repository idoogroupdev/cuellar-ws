import pytest
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from faker import Faker

from roles.models import DefaultSystemRole, Role
from users.services.user_service import UserService

fake = Faker()


@pytest.mark.django_db
def test_update_user_with_role_not_exists(setup_system_roles):
    user = UserService.create_user_with_role(
        email=fake.email(),
        password="Str0ngPass!123",
        role_name=DefaultSystemRole.CLIENT,
    )

    with pytest.raises(ValidationError):
        UserService.update_user(user, role_name="not_existing_role")


@pytest.mark.django_db
def test_update_user_with_simple_password(setup_system_roles):
    user = UserService.create_user_with_role(
        email=fake.email(),
        password="Str0ngPass!123",
        role_name=DefaultSystemRole.CLIENT,
    )

    with pytest.raises(ValidationError):
        UserService.update_user(user, password="123456")


@pytest.mark.django_db
def test_update_user_with_invalid_email(setup_system_roles):
    user = UserService.create_user_with_role(
        email=fake.email(),
        password="Str0ngPass!123",
        role_name=DefaultSystemRole.CLIENT,
    )

    with pytest.raises(ValidationError):
        UserService.update_user(user, email="invalid.email.com")


@pytest.mark.django_db
def test_update_user_with_invalid_phone(setup_system_roles):
    user = UserService.create_user_with_role(
        email=fake.email(),
        password="Str0ngPass!123",
        role_name=DefaultSystemRole.CLIENT,
    )

    with pytest.raises(ValidationError):
        UserService.update_user(user, phone="123456789")


@pytest.mark.django_db
def test_update_user_role_and_groups(setup_system_roles):
    user = UserService.create_user_with_role(
        email=fake.email(),
        password="Str0ngPass!123",
        role_name=DefaultSystemRole.CLIENT,
    )

    updated_user = UserService.update_user(user, role_name=DefaultSystemRole.ADMIN)

    assert updated_user.role == Role.objects.get(name=DefaultSystemRole.ADMIN)
    assert set(updated_user.groups.all()) == set(
        Group.objects.filter(name__in=[DefaultSystemRole.ADMIN]).all()
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role_name",
    [
        DefaultSystemRole.ADMIN,
        DefaultSystemRole.OPERATOR,
        DefaultSystemRole.BRANCH_OPERATOR,
    ],
)
def test_update_user_with_staff_role_sets_is_staff_true(setup_system_roles, role_name):
    user = UserService.create_user_with_role(
        email=fake.email(),
        password="Str0ngPass!123",
        role_name=DefaultSystemRole.CLIENT,
    )

    updated_user = UserService.update_user(user, role_name=role_name)

    assert updated_user.is_staff is True


@pytest.mark.django_db
@pytest.mark.parametrize(
    "role_name",
    [
        DefaultSystemRole.CLIENT,
        DefaultSystemRole.SALESPERSON,
        DefaultSystemRole.DELIVERY_DRIVER,
    ],
)
def test_update_user_with_non_staff_role_sets_is_staff_false(
    setup_system_roles, role_name
):
    user = UserService.create_user_with_role(
        email=fake.email(),
        password="Str0ngPass!123",
        role_name=DefaultSystemRole.ADMIN,
    )

    updated_user = UserService.update_user(user, role_name=role_name)

    assert updated_user.is_staff is False


@pytest.mark.django_db
def test_update_user_password_and_extra_fields(setup_system_roles):
    user = UserService.create_user_with_role(
        email=fake.email(),
        password="Str0ngPass!123",
        role_name=DefaultSystemRole.CLIENT,
        first_name="Old",
    )

    updated_user = UserService.update_user(
        user,
        password="N3wStr0ngPass!123",
        first_name="New",
    )

    assert updated_user.check_password("N3wStr0ngPass!123")
    assert updated_user.first_name == "New"


@pytest.mark.django_db
def test_update_user_field_not_nullable(setup_system_roles):
    user = UserService.create_user_with_role(
        email=fake.email(),
        password="Str0ngPass!123",
        role_name=DefaultSystemRole.CLIENT,
    )

    UserService.update_user(user, last_name=None)


@pytest.mark.django_db
def test_update_user_field_not_overrides(setup_system_roles):
    user = UserService.create_user_with_role(
        email=fake.email(),
        password="Str0ngPass!123",
        role_name=DefaultSystemRole.CLIENT,
        first_name="Name",
    )

    user = UserService.update_user(user, first_name=None)

    assert user.first_name == "Name"


@pytest.mark.django_db
def test_update_user_boolean_field_none(setup_system_roles):
    user = UserService.create_user_with_role(
        email=fake.email(),
        password="Str0ngPass!123",
        role_name=DefaultSystemRole.CLIENT,
        first_name="Name",
    )

    user = UserService.update_user(user, is_active=None)

    assert user.is_active is True
