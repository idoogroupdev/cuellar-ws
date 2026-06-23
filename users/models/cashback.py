from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Case, DecimalField, F, Q, Sum, When
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _

from users.models.user import User
from utils.constants import DEFAULT_AMOUNT


class CashbackHistoryQuerySet(models.QuerySet):
    def _balance_case(self):
        return Case(
            When(
                type__in=[
                    CashbackHistory.TypeChoices.EARNED,
                    CashbackHistory.TypeChoices.RELEASED,
                ],
                then=F("amount"),
            ),
            When(
                type__in=[
                    CashbackHistory.TypeChoices.SPENT,
                    CashbackHistory.TypeChoices.RESERVED,
                ],
                then=-F("amount"),
            ),
            default=DEFAULT_AMOUNT,
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )

    def cashback_balance(self):
        return self.aggregate(
            cashback_balance=Coalesce(
                Sum(
                    self._balance_case(),
                ),
                DEFAULT_AMOUNT,
            )
        )["cashback_balance"]


class CashbackHistory(models.Model):
    class TypeChoices(models.TextChoices):
        EARNED = "EARNED", _("Earned")
        SPENT = "SPENT", _("Spent")
        RESERVED = "RESERVED", _("Reserved")
        RELEASED = "RELEASED", _("Released")

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cashback_history"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=8, choices=TypeChoices.choices)
    balance_after = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    released_with = models.OneToOneField(
        "self", on_delete=models.PROTECT, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CashbackHistoryQuerySet.as_manager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(amount__gt=0),
                name="check_cashback_history_amount_gt_zero",
            ),
            models.CheckConstraint(
                condition=Q(released_with__isnull=True) | Q(type="RESERVED"),
                name="released_with_only_for_reserved_type",
            ),
        ]

    def clean(self):
        if self.released_with:
            if self.type != self.TypeChoices.RESERVED:
                raise ValidationError(
                    {"released_with": _("Cannot be used with a non-reserved type")}
                )

            if self.released_with.type != self.TypeChoices.RELEASED:
                raise ValidationError(
                    {"released_with": _("Cannot be used with a non-released type")}
                )
