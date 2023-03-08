from django.db import models

from ..core.models import ModelWithDates, ModelWithSlug, PublishableModel
from ..core.permissions import EntryPermissions
from . import EntryType


class Category(ModelWithDates, ModelWithSlug):
    class Meta:
        ordering = ["name"]
        permissions = (
            (EntryPermissions.MANAGE_CATEGORIES.codename, "Manage categories."),
        )

    def __str__(self):
        return self.name


class Entry(ModelWithDates, ModelWithSlug, PublishableModel):
    type = models.CharField(choices=EntryType.CHOICES, max_length=24)
    document_number = models.CharField(max_length=256)
    document_file = models.FileField(upload_to="entry", blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="entries"
    )
    email = models.CharField(max_length=258)
    phone = models.CharField(max_length=258, null=True, blank=True)
    address = models.CharField(max_length=258, null=True, blank=True)

    class Meta:
        ordering = ["name"]
        permissions = ((EntryPermissions.MANAGE_ENTRIES.codename, "Manage entries."),)

    def __str__(self):
        return self.name
