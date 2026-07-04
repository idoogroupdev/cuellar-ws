from django.db import models
from django.db.models import Case, Exists, IntegerField, OuterRef, When
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class BranchQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def with_pickup_enabled(self):
        return (
            self.active()
            .filter(
                is_pickup_enabled=True,
            )
            .filter(Exists(BranchHour.objects.open_now().filter(branch=OuterRef("pk"))))
        )


class Branch(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True, default=None)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pickup_enabled = models.BooleanField(default=True)

    objects = BranchQuerySet.as_manager()

    def __str__(self):
        return self.name


class BranchHourQuerySet(models.QuerySet):
    def with_ordered_by_day_of_week(self):
        return self.annotate(
            day_order=Case(
                When(day_of_week="SUNDAY", then=0),
                When(day_of_week="MONDAY", then=1),
                When(day_of_week="TUESDAY", then=2),
                When(day_of_week="WEDNESDAY", then=3),
                When(day_of_week="THURSDAY", then=4),
                When(day_of_week="FRIDAY", then=5),
                When(day_of_week="SATURDAY", then=6),
                output_field=IntegerField(),
            )
        ).order_by("day_order")

    def open_now(self):
        now = timezone.now()
        current_time = now.time()
        day_of_week = now.strftime("%A").upper()

        return self.filter(
            day_of_week=day_of_week,
            from_hour__lte=current_time,
            to_hour__gte=current_time,
        )


class BranchHour(models.Model):
    class DayOfWeekChoices(models.TextChoices):
        SUNDAY = "SUNDAY", _("Sunday")
        MONDAY = "MONDAY", _("Monday")
        TUESDAY = "TUESDAY", _("Tuesday")
        WEDNESDAY = "WEDNESDAY", _("Wednesday")
        THURSDAY = "THURSDAY", _("Thursday")
        FRIDAY = "FRIDAY", _("Friday")
        SATURDAY = "SATURDAY", _("Saturday")

    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="branch_hours",
        verbose_name=_("branch"),
    )
    day_of_week = models.CharField(
        _("day of week"), choices=DayOfWeekChoices.choices, max_length=9
    )
    from_hour = models.TimeField()
    to_hour = models.TimeField()

    objects = BranchHourQuerySet.as_manager()

    class Meta:
        unique_together = ("branch", "day_of_week")
        verbose_name = _("branch hour")
        verbose_name_plural = _("branches hours")

    def __str__(self):
        return f"{self.day_of_week} {self.from_hour} - {self.to_hour}"
