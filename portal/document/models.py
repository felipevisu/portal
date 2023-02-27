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
    expires = models.BooleanField(default=False)
    default_file = models.OneToOneField(
        "DocumentFile",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="+",
    )
    objects = models.Manager()

    class Meta:
        ordering = ["-created"]
        permissions = (
            (DocumentPermissions.MANAGE_DOCUMENTS.codename, "Manage documents."),
        )

    def __str__(self):
        return self.name


class DocumentFile(ModelWithDates):
    file = models.FileField(upload_to="documents")
    begin_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    document = models.ForeignKey(
        Document, on_delete=models.SET_NULL, null=True, related_name="files"
    )

    class Meta:
        ordering = ["-created"]
        permissions = (
            (DocumentPermissions.MANAGE_DOCUMENTS.codename, "Manage documents."),
        )

    def delete(self, using=None, keep_parents=False):
        self.file.storage.delete(self.file.name)
        super().delete()

    def extension(self):
        _, extension = os.path.splitext(self.file.name)
        return extension
