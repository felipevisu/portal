from django.core.exceptions import ValidationError
from django.db import models

from ..core.models import ModelWithDates, PublishableModel
from ..core.permissions import InvestmentPermissions


def validate_month(value):
    if value > 12 or value < 1:
        raise ValidationError("Valor inválido", params={"value": value})


class Investment(ModelWithDates, PublishableModel):
    month = models.PositiveIntegerField(validators=[validate_month])
    year = models.PositiveIntegerField()

    objects = models.Manager()

    class Meta:
        ordering = ["-year", "-month"]
        unique_together = ("year", "month")
        permissions = (
            (InvestmentPermissions.MANAGE_INVESTMENTS.codename, "Manage investments."),
        )

    def __str__(self):
        return f"{self.month}/{self.year}"


class Item(models.Model):
    name = models.CharField(max_length=256)
    value = models.DecimalField(decimal_places=2, max_digits=10)
    investment = models.ForeignKey(
        Investment, on_delete=models.CASCADE, related_name="items"
    )

    class Meta:
        ordering = ["investment", "name"]
        permissions = ((InvestmentPermissions.MANAGE_ITEMS.codename, "Manage items."),)

    def __str__(self):
        return self.name
