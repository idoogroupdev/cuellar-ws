from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from branches.models import Branch, BranchHour


class BranchHourService:
    @staticmethod
    def _get_value(data, key):
        if isinstance(data, dict):
            return data.get(key)
        return getattr(data, key, None)

    @staticmethod
    def _validate_branch(branch: Branch | int) -> Branch:
        if isinstance(branch, Branch):
            return branch

        branch_instance = Branch.objects.filter(id=branch).first()

        if not branch_instance:
            raise ValidationError(
                {"branch": _("Branch not found: %(branch)s") % {"branch": branch}}
            )

        return branch_instance

    @staticmethod
    @transaction.atomic
    def sync(branch: Branch | int, hours: list[dict]) -> list[BranchHour]:
        branch = BranchHourService._validate_branch(branch)
        valid_days = {choice for choice, _ in BranchHour.DayOfWeekChoices.choices}
        synced_hours = []
        synced_days = set()

        for hour_data in hours:
            day_of_week = BranchHourService._get_value(hour_data, "day_of_week")
            from_hour = BranchHourService._get_value(hour_data, "from_hour")
            to_hour = BranchHourService._get_value(hour_data, "to_hour")

            if day_of_week not in valid_days:
                raise ValidationError({"day_of_week": _("Invalid day of week")})

            if day_of_week in synced_days:
                raise ValidationError({"day_of_week": _("Day of week is duplicated")})

            branch_hour = BranchHour.objects.filter(
                branch=branch,
                day_of_week=day_of_week,
            ).first()

            if not branch_hour:
                branch_hour = BranchHour(branch=branch, day_of_week=day_of_week)

            branch_hour.from_hour = from_hour
            branch_hour.to_hour = to_hour
            branch_hour.full_clean()
            branch_hour.save()

            synced_hours.append(branch_hour)
            synced_days.add(day_of_week)

        BranchHour.objects.filter(branch=branch).exclude(
            day_of_week__in=synced_days
        ).delete()

        return synced_hours
