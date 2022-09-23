from django.db import models

from ..core.models import (
    ModelWithContactInfo,
    ModelWithDates,
    ModelWithSlug,
    PublishableModel,
)
from ..core.permissions import EntryPermissions
from . import EntryType


class Category(ModelWithDates, ModelWithSlug):
    type = models.CharField(choices=EntryType.CHOICES, max_length=24)

    class Meta:
        ordering = ["name"]
        permissions = (
            (EntryPermissions.MANAGE_CATEGORIES.codename, "Manage categories."),
        )

    def __str__(self):
        return self.name


class Entry(ModelWithDates, ModelWithSlug, ModelWithContactInfo, PublishableModel):
    type = models.CharField(choices=EntryType.CHOICES, max_length=24)
    document_number = models.CharField(max_length=256)
    document_file = models.FileField(upload_to="entry", blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="entries"
    )

    class Meta:
        ordering = ["name"]
        permissions = ((EntryPermissions.MANAGE_ENTRIES.codename, "Manage entries."),)

    def __str__(self):
        return self.name
