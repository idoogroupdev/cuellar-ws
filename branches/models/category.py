from django.db import models
from django.utils.translation import gettext_lazy as _


class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)


class Category(models.Model):
    name = models.CharField(verbose_name=_("name"), max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.IntegerField(default=0)
    parent = models.ForeignKey(
        "self",
        verbose_name=_("parent category"),
        related_name="subcategories",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )

    objects = CategoryQuerySet.as_manager()

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "name"],
                name="unique_category_name_per_parent",
            )
        ]
        ordering = ["sort_order"]

    def __str__(self):
        return self.name
