from branches.models import Category
from utils.functions.normalize_nullable_field_value import (
    normalize_nullable_field_value,
)


class CategoryService:
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
