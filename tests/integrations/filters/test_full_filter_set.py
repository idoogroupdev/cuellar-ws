import pytest
from django_filters import BooleanFilter, OrderingFilter

from users.models import User
from utils.filters import FullFilterSet, get_lookups


class UserFilter(FullFilterSet):
    is_active = BooleanFilter()
    order_by = OrderingFilter(fields=("email", "first_name"))

    class Meta:
        model = User
        fields = {
            "first_name": ["icontains"],
            "last_name": ["icontains"],
            "email": ["icontains"],
            "is_active": ["exact"],
        }
        or_fields = {
            "first_name": ["icontains"],
            "last_name": ["icontains"],
            "email": ["icontains"],
        }


def create_user(email, first_name, last_name, is_active=True):
    return User.objects.create_user(
        username=email,
        email=email,
        password="123456Dfddfe",
        first_name=first_name,
        last_name=last_name,
        is_active=is_active,
    )


def filter_emails(data):
    filterset = UserFilter(data=data, queryset=User.objects.all())

    assert filterset.is_valid(), filterset.errors

    return list(filterset.qs.values_list("email", flat=True))


def test_get_lookups_builds_exact_and_expression_lookups():
    assert get_lookups(
        {
            "first_name": ["icontains"],
            "is_active": ["exact"],
        }
    ) == ["first_name__icontains", "is_active"]


@pytest.mark.django_db
def test_full_filter_set_uses_or_for_meta_or_fields():
    create_user("juan@example.com", "Juan", "Gomez")
    create_user("maria@example.com", "Maria", "Pedro")
    create_user("ana@example.com", "Ana", "Lopez")

    emails = filter_emails(
        {
            "first_name__icontains": "Juan",
            "last_name__icontains": "Pedro",
            "order_by": "email",
        }
    )

    assert emails == ["juan@example.com", "maria@example.com"]


@pytest.mark.django_db
def test_full_filter_set_combines_or_fields_with_and_fields():
    create_user("active@example.com", "Juan", "Gomez", is_active=True)
    create_user("inactive-name@example.com", "Juan", "Gomez", is_active=False)
    create_user("inactive-last@example.com", "Maria", "Pedro", is_active=False)

    emails = filter_emails(
        {
            "first_name__icontains": "Juan",
            "last_name__icontains": "Pedro",
            "is_active": "false",
            "order_by": "email",
        }
    )

    assert emails == ["inactive-last@example.com", "inactive-name@example.com"]
