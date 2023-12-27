from django.db import models
from django.db.models import Exists, OuterRef

from ..core.models import SortableModel
from ..core.permissions import AttributePermissions
from ..entry.models import Entry, EntryType
from . import AttributeEntityType, AttributeInputType, AttributeType


class BaseAttributeQuerySet(models.QuerySet):
    def get_public_attributes(self):
        raise NotImplementedError

    def get_visible_to_user(self, user):
        if user:
            return self.all()
        return self.get_public_attributes()


class AssociatedAttributeQuerySet(BaseAttributeQuerySet):
    def get_public_attributes(self):
        attributes = Attribute.objects.filter(visible_in_website=True)
        return self.filter(Exists(attributes.filter(id=OuterRef("attribute_id"))))


AssociatedAttributeManager = models.Manager.from_queryset(AssociatedAttributeQuerySet)


class AttributeQuerySet(BaseAttributeQuerySet):
    def get_public_attributes(self):
        return self.filter(visible_in_website=True)

    def get_unassigned_entry_type_attributes(self, entry_type_pk: int):
        return self.entry_type_attributes().exclude(
            attributeentry__entry_type_id=entry_type_pk
        )

    def get_assigned_entry_type_attributes(self, entry_type_pk: int):
        return self.entry_type_attributes().filter(
            attributeentry__entry_type_id=entry_type_pk
        )

    def entry_type_attributes(self):
        return self.filter(type=AttributeType.ENTRY_TYPE)


AttributeManager = models.Manager.from_queryset(AttributeQuerySet)


class BaseAssignedAttribute(models.Model):
    class Meta:
        abstract = True

    @property
    def attribute(self):
        return self.assignment.attribute


class AssignedEntryAttributeValue(models.Model):
    value = models.ForeignKey(
        "AttributeValue",
        on_delete=models.CASCADE,
        related_name="entryvalueassignment",
    )
    entry = models.ForeignKey(
        Entry,
        related_name="attributevalues",
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        db_index=False,
    )

    class Meta:
        unique_together = (("value", "entry"),)
        ordering = ("pk",)


class AttributeEntry(models.Model):
    attribute = models.ForeignKey(
        "Attribute", related_name="attributeentry", on_delete=models.CASCADE
    )
    entry_type = models.ForeignKey(
        EntryType, related_name="attributeentry", on_delete=models.CASCADE
    )

    objects = AssociatedAttributeManager()

    class Meta:
        unique_together = (("attribute", "entry_type"),)
        ordering = ("pk",)


class Attribute(models.Model):
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=AttributeType.CHOICES)
    input_type = models.CharField(
        max_length=50,
        choices=AttributeInputType.CHOICES,
        default=AttributeInputType.DROPDOWN,
    )
    entity_type = models.CharField(
        max_length=50, choices=AttributeEntityType.CHOICES, blank=True, null=True
    )
    entry_types = models.ManyToManyField(
        EntryType,
        blank=True,
        related_name="entry_attributes",
        through="attribute.AttributeEntry",
        through_fields=("attribute", "entry_type"),
    )

    value_required = models.BooleanField(default=False, blank=True)
    visible_in_website = models.BooleanField(default=True, blank=True)

    filterable_in_website = models.BooleanField(default=False, blank=True)
    filterable_in_dashboard = models.BooleanField(default=False, blank=True)

    website_search_position = models.IntegerField(default=0, blank=True)
    available_in_grid = models.BooleanField(default=False, blank=True)

    objects = AttributeManager()

    class Meta:
        ordering = ("name",)
        permissions = (
            (AttributePermissions.MANAGE_ATTRIBUTES.codename, "Manage attributes."),
        )

    def __str__(self) -> str:
        return self.name

    def has_values(self) -> bool:
        return self.values.exists()


class AttributeValue(SortableModel):
    name = models.CharField(max_length=250)
    value = models.CharField(max_length=100, blank=True, default="")
    slug = models.SlugField(max_length=255, allow_unicode=True)
    file_url = models.URLField(null=True, blank=True)
    content_type = models.CharField(max_length=50, null=True, blank=True)
    attribute = models.ForeignKey(
        Attribute, related_name="values", on_delete=models.CASCADE
    )
    plain_text = models.TextField(
        blank=True,
        null=True,
    )
    boolean = models.BooleanField(blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)
    reference = models.ForeignKey(
        Entry,
        related_name="references",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("name",)
        unique_together = ("slug", "attribute")

    def __str__(self) -> str:
        return self.name

    @property
    def input_type(self):
        return self.attribute.input_type

    def get_ordering_queryset(self):
        return self.attribute.values.all()
