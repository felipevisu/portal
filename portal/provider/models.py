from django.db import models

from ..core.models import (
    ModelWithContactInfo,
    ModelWithDates,
    ModelWithSlug,
    PublishableModel,
)
from ..core.permissions import ProviderPermissions


class Segment(ModelWithDates, ModelWithSlug):
    class Meta:
        ordering = ["name"]
        permissions = (
            (ProviderPermissions.MANAGE_SEGMENTS.codename, "Manage segments."),
        )

    def __str__(self):
        return self.name


class Provider(ModelWithDates, ModelWithSlug, ModelWithContactInfo, PublishableModel):
    document_number = models.CharField(max_length=256)
    segment = models.ForeignKey(
        Segment, on_delete=models.PROTECT, related_name="providers"
    )

    class Meta:
        ordering = ["name"]
        permissions = (
            (ProviderPermissions.MANAGE_PROVIDERS.codename, "Manage providers."),
        )

    def __str__(self):
        return self.name
