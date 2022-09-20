from django.db import models

from ..core.models import (
    ModelWithContactInfo,
    ModelWithDates,
    ModelWithSlug,
    PublishableModel,
)
from ..core.permissions import VehiclePermissions


class Category(ModelWithDates, ModelWithSlug):
    class Meta:
        ordering = ["name"]
        permissions = (
            (VehiclePermissions.MANAGE_CATEGORIES.codename, "Manage categories."),
        )

    def __str__(self):
        return self.name


class Vehicle(ModelWithDates, ModelWithSlug, ModelWithContactInfo, PublishableModel):
    document_number = models.CharField(max_length=256)
    document_file = models.FileField(upload_to="vehicle", blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="vehicles"
    )

    class Meta:
        ordering = ["name"]
        permissions = (
            (VehiclePermissions.MANAGE_VEHICLES.codename, "Manage vehicles."),
        )

    def __str__(self):
        return self.name
