import pytest
from django.core.exceptions import ValidationError

from branches.models import Category
from branches.services.category_service import CategoryService


@pytest.mark.django_db
def test_sync_subcategories_creates_categories():
    parent = CategoryService.create(name="Parent")

    subcategories = CategoryService.sync_subcategories(parent.id, ["Candy", "Cookies"])

    assert len(subcategories) == 2
    assert Category.objects.filter(parent=parent).count() == 2
    assert list(
        Category.objects.filter(parent=parent).values_list("name", "sort_order")
    ) == [
        ("Candy", 0),
        ("Cookies", 1),
    ]


@pytest.mark.django_db
def test_sync_subcategories_updates_order_and_deletes_missing_categories():
    parent = CategoryService.create(name="Parent")
    CategoryService.create(name="Candy", parent=parent, sort_order=0)
    CategoryService.create(name="Cookies", parent=parent, sort_order=1)
    CategoryService.create(name="Chocolate", parent=parent, sort_order=2)

    CategoryService.sync_subcategories(parent, ["Chocolate", "Candy"])

    assert list(
        Category.objects.filter(parent=parent).values_list("name", "sort_order")
    ) == [
        ("Chocolate", 0),
        ("Candy", 1),
    ]
    assert not Category.objects.filter(parent=parent, name="Cookies").exists()


@pytest.mark.django_db
def test_sync_subcategories_does_not_delete_other_parent_subcategories():
    parent = CategoryService.create(name="Parent")
    another_parent = CategoryService.create(name="Another Parent")
    CategoryService.create(name="Candy", parent=parent)
    other_subcategory = CategoryService.create(name="Gum", parent=another_parent)

    CategoryService.sync_subcategories(parent.id, [])

    assert not Category.objects.filter(parent=parent).exists()
    assert Category.objects.filter(id=other_subcategory.id).exists()


@pytest.mark.django_db
def test_sync_subcategories_raises_validation_error_with_invalid_parent():
    with pytest.raises(ValidationError):
        CategoryService.sync_subcategories(999, ["Candy"])


@pytest.mark.django_db
def test_sync_subcategories_raises_validation_error_with_duplicated_name():
    parent = CategoryService.create(name="Parent")

    with pytest.raises(ValidationError):
        CategoryService.sync_subcategories(parent, ["Candy", "Candy"])
