from typing import cast

import graphene
from django.db.models import QuerySet

from ...attribute import AttributeInputType, models
from ..core.connection import (
    CountableConnection,
    create_connection_slice,
    filter_connection_queryset,
)
from ..core.fields import ConnectionField, FilterConnectionField
from ..core.types import File, ModelObjectType, NonNullList
from ..core.types.common import DateRangeInput, DateTimeRangeInput, IntRangeInput
from ..decorators import check_required_permissions
from .dataloaders import AttributesByAttributeId
from .enums import AttributeInputTypeEnum, AttributeTypeEnum
from .filters import AttributeValueFilterInput
from .sorters import AttributeChoicesSortingInput


class AttributeValueSelectableTypeInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    value = graphene.String(required=False)


class AttributeValueInput(graphene.InputObjectType):
    id = graphene.ID()
    values = NonNullList(graphene.String, required=False)
    dropdown = AttributeValueSelectableTypeInput(required=False)
    multiselect = NonNullList(AttributeValueSelectableTypeInput, required=False)
    plain_text = graphene.String(required=False)
    boolean = graphene.Boolean(required=False)
    date = graphene.Date(required=False)


class AttributeValue(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String()
    slug = graphene.String()
    value = graphene.String()
    input_type = AttributeInputTypeEnum()
    file = graphene.Field(File, required=False)
    plain_text = graphene.String(required=False)
    boolean = graphene.Boolean(required=False)
    date = graphene.Date(required=False)
    date_time = graphene.DateTime(required=False)

    class Meta:
        interfaces = [graphene.relay.Node]
        model = models.AttributeValue

    @staticmethod
    def resolve_input_type(root, info):
        return (
            AttributesByAttributeId(info.context)
            .load(root.attribute_id)
            .then(lambda attribute: attribute.input_type)
        )

    @staticmethod
    def resolve_date_time(root, info):
        def _resolve_date(attribute):
            if attribute.input_type == AttributeInputType.DATE_TIME:
                return root.date_time
            return None

        return (
            AttributesByAttributeId(info.context)
            .load(root.attribute_id)
            .then(_resolve_date)
        )

    @staticmethod
    def resolve_date(root, info):
        def _resolve_date(attribute):
            if attribute.input_type == AttributeInputType.DATE:
                return root.date_time
            return None

        return (
            AttributesByAttributeId(info.context)
            .load(root.attribute_id)
            .then(_resolve_date)
        )


class AttributeValueCountableConnection(CountableConnection):
    class Meta:
        node = AttributeValue


class Attribute(ModelObjectType):
    id = graphene.GlobalID(required=True)
    type = AttributeTypeEnum()
    input_type = AttributeInputTypeEnum()
    name = graphene.String()
    slug = graphene.String()
    choices = FilterConnectionField(
        AttributeValueCountableConnection,
        sort_by=AttributeChoicesSortingInput(),
        filter=AttributeValueFilterInput(),
    )
    with_choices = graphene.Boolean(required=True)
    value_required = graphene.Boolean(required=True)
    visible_in_website = graphene.Boolean(required=True)
    filterable_in_website = graphene.Boolean(required=True)
    filterable_in_dashboard = graphene.Boolean(required=True)
    documents = ConnectionField(
        "portal.graphql.document.types.DocumentCountableConnection",
        required=True,
    )
    entries = ConnectionField(
        "portal.graphql.entry.types.EntryCountableConnection",
        required=True,
    )

    class Meta:
        interfaces = [graphene.relay.Node]
        model = models.Attribute

    @staticmethod
    def resolve_choices(root, info, **kwargs):
        if root.input_type in AttributeInputType.TYPES_WITH_CHOICES:
            qs = cast(QuerySet[models.AttributeValue], root.values.all())
        else:
            qs = cast(
                QuerySet[models.AttributeValue], models.AttributeValue.objects.none()
            )

        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(
            qs, info, kwargs, AttributeValueCountableConnection
        )

    @staticmethod
    @check_required_permissions()
    def resolve_value_required(root, _info):
        return root.value_required

    @staticmethod
    @check_required_permissions()
    def resolve_visible_in_website(root: models.Attribute, _info):
        return root.visible_in_website

    @staticmethod
    @check_required_permissions()
    def resolve_filterable_in_website(root: models.Attribute, _info):
        return root.filterable_in_website

    @staticmethod
    @check_required_permissions()
    def resolve_filterable_in_dashboard(root: models.Attribute, _info):
        return root.filterable_in_dashboard

    @staticmethod
    def resolve_with_choices(root: models.Attribute, _info):
        return root.input_type in AttributeInputType.TYPES_WITH_CHOICES

    @staticmethod
    def resolve_entries(root: models.Attribute, info, **kwargs):
        from ..entry.types import EntryCountableConnection

        qs = root.entries.all()
        return create_connection_slice(qs, info, kwargs, EntryCountableConnection)

    @staticmethod
    def resolve_documents(root: models.Attribute, info, **kwargs):
        from ..document.types import DocumentCountableConnection

        qs = root.documents.all()
        return create_connection_slice(qs, info, kwargs, DocumentCountableConnection)


class AttributeCountableConnection(CountableConnection):
    class Meta:
        node = Attribute


class SelectedAttribute(graphene.ObjectType):
    attribute = graphene.Field(Attribute, default_value=None, required=True)
    values = NonNullList(AttributeValue, required=True)

    class Meta:
        description = "Represents a custom attribute."


class AttributeInput(graphene.InputObjectType):
    slug = graphene.String(required=True)
    values = NonNullList(graphene.String, required=False)
    values_range = graphene.Field(IntRangeInput, required=False)
    date_time = graphene.Field(DateTimeRangeInput, required=False)
    date = graphene.Field(DateRangeInput, required=False)
    boolean = graphene.Boolean(required=False)


class AttributeValueSelectableTypeInput(graphene.InputObjectType):
    id = graphene.ID(required=False)
    value = graphene.String(required=False)


class AttributeValueInput(graphene.InputObjectType):
    id = graphene.ID()
    values = NonNullList(graphene.String, required=False)
    dropdown = AttributeValueSelectableTypeInput(required=False)
    swatch = AttributeValueSelectableTypeInput(required=False)
    multiselect = NonNullList(AttributeValueSelectableTypeInput, required=False)
    numeric = graphene.String(required=False)
    file = graphene.String(required=False)
    content_type = graphene.String(required=False)
    plain_text = graphene.String(required=False)
    boolean = graphene.Boolean(required=False)
    date = graphene.Date(required=False)
    date_time = graphene.DateTime(required=False)
