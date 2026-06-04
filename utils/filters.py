from django.db.models import Q
from django_filters import FilterSet


def get_lookups(fields: dict):
    lookups = []

    for field, expressions in fields.items():
        for expression in expressions:
            lookups.append(field if expression == "exact" else f"{field}__{expression}")

    return lookups


class FullFilterSet(FilterSet):
    class Meta:
        or_fields = {}

    def filter_queryset(self, queryset):
        order = self.form.cleaned_data.get("order_by") or []

        all_lookups = get_lookups(self.get_fields())
        or_lookups = get_lookups(getattr(self.Meta, "or_fields", {}))

        or_q = Q()
        and_q = Q()

        for lookup, value in self.form.cleaned_data.items():
            if lookup == "order_by" or value is None or value == "":
                continue

            if lookup in or_lookups:
                or_q |= Q(**{lookup: value})
            elif lookup in all_lookups:
                and_q &= Q(**{lookup: value})

        queryset = queryset.filter(or_q & and_q)

        if order:
            queryset = queryset.order_by(*order)

        return queryset
