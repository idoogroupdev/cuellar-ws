from branches.models import Branch
from utils.functions.normalize_nullable_field_value import (
    normalize_nullable_field_value,
)


class BranchService:
    @staticmethod
    def create_branch(
        name: str,
        address: str = None,
        is_active=True,
        **extra_fields,
    ) -> Branch:

        return Branch.objects.create(
            name=name, address=address, is_active=is_active, **extra_fields
        )

    @staticmethod
    def update_branch(
        branch: Branch,
        **fields,
    ) -> Branch:
        update_fields: list[str] = []

        for field, value in fields.items():
            model_field = branch._meta.get_field(field)
            if value is None and not model_field.null:
                continue

            value = normalize_nullable_field_value(branch, field, value)

            if getattr(branch, field) != value:
                setattr(branch, field, value)
                update_fields.append(field)

        if update_fields:
            branch.full_clean()
            branch.save(update_fields=update_fields)

        return branch
