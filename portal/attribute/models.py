from django.db import models
from django.db.models import Exists, OuterRef, Q

from ..core.models import SortableModel
from ..document.models import Document
from ..entry.models import Entry
from . import AttributeInputType, AttributeType


class BaseAttributeQuerySet(models.QuerySet):
    def get_public_attributes(self):
        raise NotImplementedError

    def get_visible_to_user(self, user):
        if user.is_staff:
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

    def document_attributes(self):
        return self.filter(type=AttributeType.DOCUMENT)

    def entry_attributes(self):
        return self.filter(type=AttributeType.ENTRY)


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
    assignment = models.ForeignKey(
        "AssignedEntryAttribute",
        on_delete=models.CASCADE,
        related_name="entryvalueassignment",
    )

    class Meta:
        unique_together = (("value", "assignment"),)
        ordering = ("pk",)


class AssignedDocumentAttributeValue(models.Model):
    value = models.ForeignKey(
        "AttributeValue",
        on_delete=models.CASCADE,
        related_name="documentvalueassignment",
    )
    assignment = models.ForeignKey(
        "AssignedDocumentAttribute",
        on_delete=models.CASCADE,
        related_name="documentvalueassignment",
    )

    class Meta:
        unique_together = (("value", "assignment"),)
        ordering = ("pk",)


class AssignedEntryAttribute(BaseAssignedAttribute):
    entry = models.ForeignKey(
        Entry, related_name="attributes", on_delete=models.CASCADE
    )
    attribute = models.ForeignKey(
        "Attribute", on_delete=models.CASCADE, related_name="entryassignments"
    )
    values = models.ManyToManyField(
        "AttributeValue",
        blank=True,
        related_name="entryassignments",
        through=AssignedEntryAttributeValue,
        through_fields=("assignment", "value"),
    )

    class Meta:
        unique_together = (("entry", "attribute"),)


class AssignedDocumentAttribute(BaseAssignedAttribute):
    document = models.ForeignKey(
        Document, related_name="attributes", on_delete=models.CASCADE
    )
    attribute = models.ForeignKey(
        "Attribute", on_delete=models.CASCADE, related_name="documentassignments"
    )
    values = models.ManyToManyField(
        "AttributeValue",
        blank=True,
        related_name="documentassignments",
        through=AssignedDocumentAttributeValue,
        through_fields=("assignment", "value"),
    )

    class Meta:
        unique_together = (("document", "attribute"),)


class Attribute(models.Model):
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=AttributeType.CHOICES)

    input_type = models.CharField(
        max_length=50,
        choices=AttributeInputType.CHOICES,
        default=AttributeInputType.DROPDOWN,
    )
    assigned_entries = models.ManyToManyField(
        Entry,
        blank=True,
        through=AssignedEntryAttribute,
        through_fields=("attribute", "entry"),
        related_name="attributesrelated",
    )
    assigned_documents = models.ManyToManyField(
        Document,
        blank=True,
        through=AssignedDocumentAttribute,
        through_fields=("attribute", "document"),
        related_name="attributesrelated",
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
    date = models.DateField(blank=True, null=True)
    date_time = models.DateTimeField(blank=True, null=True)

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
