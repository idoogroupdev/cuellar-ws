import pytest
from django.core.exceptions import ValidationError

from branches.services.category_service import CategoryService


@pytest.fixture
def category():
    return CategoryService.create(name="Test")


@pytest.mark.django_db
def test_update_category(category):
    category = CategoryService.update(
        category, name="New Name", is_active=False, sort_order=10
    )
    assert category.name == "New Name"
    assert category.is_active is False
    assert category.sort_order == 10


@pytest.mark.django_db
def test_update_category_name_duplicated(category):
    CategoryService.create(name="Test2")

    with pytest.raises(ValidationError):
        CategoryService.update(category, name="Test2")
