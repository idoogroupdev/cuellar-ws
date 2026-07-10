import pytest
from django.core.exceptions import ValidationError

from branches.services.branch_service import BranchService


@pytest.mark.django_db
def test_create_branch():
    branch = BranchService.create_branch(name="test")
    assert branch.name == "test"
    assert branch.address is None
    assert branch.is_active is True


@pytest.mark.django_db
def test_create_branch_invalid_name():
    with pytest.raises(ValidationError):
        BranchService.create_branch(name="test" * 64)
