import pytest

from branches.models import Category
from branches.services.category_service import CategoryService
from tests.autofixture import AutoFixture
from django.core.exceptions import ValidationError


@pytest.fixture
def categories():
    return AutoFixture(Category, count=3).create()


@pytest.mark.django_db
def test_reorder_category(categories):
    category_ids = [category.id for category in categories]
    category_ids.sort(reverse=True)

    CategoryService.reorder(category_ids)

    categories = Category.objects.filter(id__in=category_ids).order_by("-id")

    assert categories[0].sort_order == 0
    assert categories[1].sort_order == 1
    assert categories[2].sort_order == 2


@pytest.mark.django_db
def test_reorder_category_not_exists():
    category_ids = [3, 2, 1]

    with pytest.raises(ValidationError):
        CategoryService.reorder(category_ids)
