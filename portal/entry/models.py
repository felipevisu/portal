from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Exists, OuterRef, Q

from ..channel.models import Channel
from ..core.models import ModelWithDates, ModelWithSlug, PublishableModel
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


class EntryQueryset(models.QuerySet):
    def published(self, channel_slug: str):
        channels = Channel.objects.filter(
            slug=str(channel_slug), is_active=True
        ).values("id")
        channel_listings = EntryChannelListing.objects.filter(
            Exists(channels.filter(pk=OuterRef("channel_id"))),
            is_published=True,
        ).values("id")
        return self.filter(Exists(channel_listings.filter(product_id=OuterRef("pk"))))

    def not_published(self, channel_slug: str):
        return self.annotate_publication_info(channel_slug).filter(
            Q(is_published=False) | Q(is_published__isnull=True)
        )


EntryManager = models.Manager.from_queryset(EntryQueryset)


class Entry(ModelWithDates, ModelWithSlug):
    type = models.CharField(choices=EntryType.CHOICES, max_length=24)
    document_number = models.CharField(max_length=256)
    document_file = models.FileField(upload_to="entry", blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="entries"
    )
    email = models.CharField(max_length=258)
    phone = models.CharField(max_length=258, null=True, blank=True)
    address = models.CharField(max_length=258, null=True, blank=True)

    objects = EntryManager()

    class Meta:
        ordering = ["name"]
        permissions = ((EntryPermissions.MANAGE_ENTRIES.codename, "Manage entries."),)

    def __str__(self):
        return self.name


class EntryChannelListing(PublishableModel):
    product = models.ForeignKey(
        Entry,
        null=False,
        blank=False,
        related_name="channel_listings",
        on_delete=models.CASCADE,
    )
    channel = models.ForeignKey(
        Channel,
        null=False,
        blank=False,
        related_name="product_listings",
        on_delete=models.CASCADE,
    )
    active = models.BooleanField(default=False)

    class Meta:
        unique_together = [["entry", "channel"]]
        ordering = ("pk",)


class Consult(ModelWithDates):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE, related_name="consult")
    plugin = models.CharField(max_length=64)
    response = models.JSONField(blank=True, default=dict, encoder=DjangoJSONEncoder)

    class Meta:
        ordering = ["-created"]
