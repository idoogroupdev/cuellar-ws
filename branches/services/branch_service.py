from branches.models import Branch


class BranchService:
    @staticmethod
    def create_branch(
        name: str, address: str = None, is_active=True, **extra_fields
    ) -> Branch:

        return Branch.objects.create(
            name=name, address=address, is_active=is_active, **extra_fields
        )
