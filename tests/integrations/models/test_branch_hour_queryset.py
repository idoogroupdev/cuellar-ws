from datetime import timedelta

import pytest
from django.utils import timezone

from branches.models import BranchHour
from branches.services.branch_hour_service import BranchHourService
from branches.services.branch_service import BranchService


@pytest.mark.django_db
def test_open_now():
    BranchService.create_branch(name="Closed")
    branch_open = BranchService.create_branch(name="Open")

    now = timezone.now()
    day_of_week = now.strftime("%A").upper()

    from_hour = (now - timedelta(hours=1)).time()
    to_hour = (now + timedelta(hours=1)).time()

    BranchHourService.sync(
        branch_open,
        [{"day_of_week": day_of_week, "from_hour": from_hour, "to_hour": to_hour}],
    )

    assert BranchHour.objects.open_now().first().branch == branch_open
