import os

from django.db import models

from ..core.models import ModelWithDates, ModelWithSlug, PublishableModel
from ..core.permissions import ProviderPermissions


class Segment(ModelWithDates, ModelWithSlug):
    class Meta:
        ordering = ['name']
        permissions = (
            (ProviderPermissions.MANAGE_SEGMENTS.codename, "Manage segments."),
        )

    def __str__(self):
        return self.name


class Provider(ModelWithDates, ModelWithSlug, PublishableModel):
    document_number = models.CharField(max_length=256)
    segment = models.ForeignKey(
        Segment, on_delete=models.PROTECT, related_name="providers")

    class Meta:
        ordering = ['name']
        permissions = (
            (ProviderPermissions.MANAGE_PROVIDERS.codename, "Manage providers."),
        )

    def __str__(self):
        return self.name


class Document(ModelWithDates, ModelWithSlug, PublishableModel):
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to="documents")
    expires = models.BooleanField(default=False)
    begin_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['provider', '-created']
        permissions = (
            (ProviderPermissions.MANAGE_DOCUMENTS.codename, "Manage documents."),
        )

    def __str__(self):
        return self.name

    def extension(self):
        _, extension = os.path.splitext(self.file.name)
        return extension
