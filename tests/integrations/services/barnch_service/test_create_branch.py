import pytest

from branches.services.branch_service import BranchService


@pytest.mark.django_db
def test_create_branch():
    branch = BranchService.create_branch(name="test")
    assert branch.name == "test"
    assert branch.address is None
    assert branch.is_active is True
