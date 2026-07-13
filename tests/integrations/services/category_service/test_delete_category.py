import pytest

from branches.models import Category
from branches.services.category_service import CategoryService


@pytest.fixture
def category():
    return CategoryService.create(name="category")


@pytest.mark.django_db
def test_delete_category(category):
    CategoryService.delete(category)
    assert Category.objects.filter(id=category.id).exists() is False
