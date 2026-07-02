from datetime import time

import pytest
from django.core.exceptions import ValidationError

from branches.models import BranchHour
from branches.services.branch_hour_service import BranchHourService
from branches.services.branch_service import BranchService


@pytest.mark.django_db
def test_sync_creates_branch_hours():
    branch = BranchService.create_branch(name="Main")

    synced_hours = BranchHourService.sync(
        branch,
        [
            {
                "day_of_week": BranchHour.DayOfWeekChoices.MONDAY,
                "from_hour": time(8, 0),
                "to_hour": time(17, 0),
            },
            {
                "day_of_week": BranchHour.DayOfWeekChoices.TUESDAY,
                "from_hour": time(9, 0),
                "to_hour": time(18, 0),
            },
        ],
    )

    assert len(synced_hours) == 2
    assert BranchHour.objects.filter(branch=branch).count() == 2
    assert BranchHour.objects.get(
        branch=branch, day_of_week=BranchHour.DayOfWeekChoices.MONDAY
    ).from_hour == time(8, 0)


@pytest.mark.django_db
def test_sync_updates_existing_hours_and_deletes_missing_days():
    branch = BranchService.create_branch(name="Main")
    BranchHour.objects.create(
        branch=branch,
        day_of_week=BranchHour.DayOfWeekChoices.MONDAY,
        from_hour=time(8, 0),
        to_hour=time(17, 0),
    )
    BranchHour.objects.create(
        branch=branch,
        day_of_week=BranchHour.DayOfWeekChoices.TUESDAY,
        from_hour=time(9, 0),
        to_hour=time(18, 0),
    )

    BranchHourService.sync(
        branch.id,
        [
            {
                "day_of_week": BranchHour.DayOfWeekChoices.MONDAY,
                "from_hour": time(10, 0),
                "to_hour": time(19, 0),
            },
            {
                "day_of_week": BranchHour.DayOfWeekChoices.WEDNESDAY,
                "from_hour": time(11, 0),
                "to_hour": time(20, 0),
            },
        ],
    )

    assert list(
        BranchHour.objects.filter(branch=branch)
        .with_ordered_by_day_of_week()
        .values_list("day_of_week", flat=True)
    ) == [
        BranchHour.DayOfWeekChoices.MONDAY,
        BranchHour.DayOfWeekChoices.WEDNESDAY,
    ]
    assert BranchHour.objects.get(
        branch=branch, day_of_week=BranchHour.DayOfWeekChoices.MONDAY
    ).from_hour == time(10, 0)


@pytest.mark.django_db
def test_sync_raises_validation_error_with_invalid_day():
    branch = BranchService.create_branch(name="Main")

    with pytest.raises(ValidationError):
        BranchHourService.sync(
            branch,
            [
                {
                    "day_of_week": "NOT_A_DAY",
                    "from_hour": time(8, 0),
                    "to_hour": time(17, 0),
                }
            ],
        )


@pytest.mark.django_db
def test_sync_raises_validation_error_with_duplicated_day():
    branch = BranchService.create_branch(name="Main")

    with pytest.raises(ValidationError):
        BranchHourService.sync(
            branch,
            [
                {
                    "day_of_week": BranchHour.DayOfWeekChoices.MONDAY,
                    "from_hour": time(8, 0),
                    "to_hour": time(17, 0),
                },
                {
                    "day_of_week": BranchHour.DayOfWeekChoices.MONDAY,
                    "from_hour": time(9, 0),
                    "to_hour": time(18, 0),
                },
            ],
        )
