import os

from django.db import models

from ..core.models import ModelWithDates, PublishableModel
from ..core.permissions import DocumentPermissions
from ..entry.models import Entry


class Document(ModelWithDates, PublishableModel):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    entry = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="documents",
        null=True,
        blank=True,
    )
    file = models.FileField(upload_to="documents")
    expires = models.BooleanField(default=False)
    begin_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)

    objects = models.Manager()

    class Meta:
        ordering = ["-created"]
        permissions = (
            (DocumentPermissions.MANAGE_DOCUMENTS.codename, "Manage documents."),
        )

    def __str__(self):
        return self.name

    def extension(self):
        _, extension = os.path.splitext(self.file.name)
        return extension

    def delete(self, using=None, keep_parents=False):
        self.file.storage.delete(self.file.name)
        super().delete()
