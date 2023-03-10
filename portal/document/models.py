import os

from django.db import models
from django.utils.text import slugify

from ..core.models import ModelWithDates, PublishableModel
from ..core.permissions import DocumentPermissions
from ..entry.models import Entry
from . import DocumentFileStatus


def get_upload_path(instance, filename):
    return os.path.join(
        "entry_%d" % instance.document.entry.id,
        "document_%d" % instance.document.id,
        "{0}.{1}".format(slugify(instance.document.name), filename.split(".")[-1]),
    )


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

    class Meta:
        ordering = ["-created"]
        permissions = (
            (DocumentPermissions.MANAGE_DOCUMENTS.codename, "Manage documents."),
        )

    def __str__(self):
        return self.name


class DocumentFile(ModelWithDates):
    file = models.FileField(upload_to=get_upload_path)
    begin_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="files"
    )
    status = models.CharField(choices=DocumentFileStatus.CHOICES, max_length=100)

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
