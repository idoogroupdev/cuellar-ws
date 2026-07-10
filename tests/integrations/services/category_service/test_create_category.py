import pytest
from django.core.exceptions import ValidationError

from branches.services.category_service import CategoryService


@pytest.mark.django_db
def test_create_category():
    category = CategoryService.create(name="Test")
    assert category.name == "Test"


@pytest.mark.django_db
def test_create_category_name_duplicated():
    CategoryService.create(name="Test")

    with pytest.raises(ValidationError):
        CategoryService.create(name="Test")
