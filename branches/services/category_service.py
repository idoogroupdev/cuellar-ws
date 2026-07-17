from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from branches.models import Category
from utils.functions.normalize_nullable_field_value import (
    normalize_nullable_field_value,
)


class CategoryService:
    @staticmethod
    def _validate_category(category: Category | int) -> Category:
        if isinstance(category, Category):
            return category

        category_db = Category.objects.filter(id=category).first()

        if not category_db:
            raise ValidationError(
                {
                    "parent_id": _("Category not found: %(category)s")
                    % {"category": category}
                }
            )

        return category_db

    @staticmethod
    def create(name: str, **extra_fields):
        category = Category(name=name, **extra_fields)
        category.full_clean()
        category.save()
        return category

    @staticmethod
    def update(category: Category, **fields):
        update_fields: list[str] = []

        for field, value in fields.items():
            model_field = category._meta.get_field(field)
            if value is None and not model_field.null:
                continue

            value = normalize_nullable_field_value(category, field, value)

            if getattr(category, field) != value:
                setattr(category, field, value)
                update_fields.append(field)

        if update_fields:
            category.full_clean()
            category.save(update_fields=update_fields)

        return category

    @staticmethod
    def reorder(category_ids: list[int]):

        categories = {
            category.id: category
            for category in Category.objects.filter(id__in=category_ids)
        }

        if len(categories) != len(category_ids):
            raise ValidationError({"ids": _("One or more categories do not exist.")})

        updates = []

        for index, category_id in enumerate(category_ids):
            category = categories[category_id]
            if category.sort_order != index:
                category.sort_order = index
                updates.append(category)

        if updates:
            Category.objects.bulk_update(updates, ["sort_order"])

    @staticmethod
    @transaction.atomic
    def sync_subcategories(parent: Category | int, names: list[str]) -> list[Category]:
        parent = CategoryService._validate_category(parent)
        synced_subcategories = []
        synced_names = set()

        for index, name in enumerate(names):
            if name in synced_names:
                raise ValidationError({"names": _("Category name is duplicated")})

            subcategory = Category.objects.filter(parent=parent, name=name).first()

            if not subcategory:
                subcategory = Category(parent=parent, name=name)

            subcategory.sort_order = index
            subcategory.full_clean()
            subcategory.save()

            synced_subcategories.append(subcategory)
            synced_names.add(name)

        Category.objects.filter(parent=parent).exclude(name__in=synced_names).delete()

        return synced_subcategories

    @staticmethod
    def delete(category: Category):
        category.delete()
