import inspect
from datetime import timedelta
from decimal import Decimal
from random import choice
from string import ascii_lowercase
from typing import Generic, TypeVar

from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.db import models
from django.db.models import Field
from django.utils import timezone
from faker import Faker

fake = Faker()


DEFAULT_FIELD_FACTORIES = {
    models.JSONField: lambda f: {},
    models.DecimalField: lambda f: fake.pydecimal(
        left_digits=f.max_digits - f.decimal_places,
        right_digits=f.decimal_places,
        min_value=Decimal("0"),
        max_value=Decimal("100"),
    ),
    models.DurationField: lambda f: timedelta(minutes=fake.random_int(1, 60)),
    models.TimeField: lambda f: fake.time(),
    models.EmailField: lambda f: (
        fake.email(safe=False) + choice([x for x in ascii_lowercase])
    ),
    models.TextField: lambda f: fake.paragraph(),
    models.CharField: lambda f: fake.pystr(max_chars=f.max_length),
    models.IntegerField: lambda f: fake.random_int(),
    models.FloatField: lambda f: fake.pyfloat(),
    models.BooleanField: lambda f: f.get_default(),
    models.DateField: lambda f: timezone.now().date(),
    models.DateTimeField: lambda f: timezone.now(),
    models.UUIDField: lambda f: fake.uuid4(),
    gis_models.PointField: lambda f: Point(
        int(fake.longitude()), int(fake.latitude()), srid=f.srid or 4326
    ),
}

T = TypeVar("T")


class AutoFixture(Generic[T]):
    """
    Example:
    ```python
    AutoFixture(User, count=10).create()

    AutoFixture(
        Post,
        count=5,
        overrides={
            "title": lambda: "Post title",
            "published":  True,
        }
    ).create()
    ```
    """

    def __init__(
        self,
        model: type[T],
        count=1,
        overrides=None,
        max_depth=3,
        skips_fields=["password", "released_with"],
    ):
        self.model = model
        self.count = count
        self.overrides = overrides or {}
        self.max_depth = max_depth
        self.skips_fields = skips_fields

    def create(self) -> T | list[T]:
        instances: list[T] = []

        for _ in range(self.count):
            instances.append(self._create_instance())

        return instances[0] if self.count == 1 else instances

    def _create_instance(self, depth=0) -> T:
        data = {}

        for name, factory in self.overrides.items():
            data[name] = factory() if inspect.isfunction(factory) else factory

        for field in self.model._meta.concrete_fields:
            if isinstance(field, Field):
                if (
                    field.name in data
                    or field.auto_created
                    or field.name in self.skips_fields
                ):
                    continue

                if isinstance(field, models.OneToOneField):
                    data[field.name] = self._handle_fk(
                        field, depth, reuse_existing=False
                    )
                    continue

                if isinstance(field, models.ForeignKey):
                    data[field.name] = self._handle_fk(field, depth)
                    continue

                value = self._fake_value_for_field(field)
                if value is not None:
                    data[field.name] = value

        instance = self.model.objects.create(**data)
        self._handle_m2m(instance, depth)
        return instance

    def _fake_value_for_field(self, field):

        # NOTE: This is a hack to generate fake names
        if isinstance(field, models.CharField) and "name" in field.name:
            return fake.name()

        for field_type, factory in DEFAULT_FIELD_FACTORIES.items():
            if isinstance(field, field_type):
                return factory(field)
        return None

    def _handle_fk(self, field: Field, depth, reuse_existing=True):
        related = field.related_model

        obj_cached = related.objects.order_by("?").first()

        if depth >= self.max_depth:
            return obj_cached if reuse_existing else None

        if reuse_existing and obj_cached:
            return obj_cached

        return AutoFixture(
            related,
            max_depth=self.max_depth,
        )._create_instance(depth + 1)

    def _handle_m2m(self, instance, depth):
        if depth >= self.max_depth:
            return

        for field in instance._meta.many_to_many:
            if field.name in self.skips_fields:
                continue

            related = field.related_model

            objs = list(related.objects.order_by("?")[: fake.random_int(1, 3)])

            if not objs:
                objs = [
                    AutoFixture(
                        related,
                        max_depth=self.max_depth,
                    )._create_instance(depth + 1)
                    for _ in range(fake.random_int(1, 3))
                ]

            getattr(instance, field.name).add(*objs)
