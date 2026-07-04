import pytest

from branches.services.branch_service import BranchService


@pytest.mark.django_db
def test_update_branch():
    branch = BranchService.create_branch(name="test")
    assert branch.name == "test"
    assert branch.address is None
    assert branch.is_active is True

    BranchService.update_branch(branch, name="test2", is_active=False)
    assert branch.name == "test2"
    assert branch.address is None
    assert branch.is_active is False
