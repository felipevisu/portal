import graphene

from ...attribute import models
from ..core.connection import create_connection_slice, filter_connection_queryset
from ..core.fields import FilterConnectionField
from .filters import AttributeFilterInput
from .mutations import (
    AttributeCreate,
    AttributeDelete,
    AttributeUpdate,
    AttributeValueCreate,
    AttributeValueDelete,
    AttributeValueUpdate,
)
from .resolvers import resolve_attribute, resolve_attributes
from .sorters import AttributeSortingInput
from .types import Attribute, AttributeCountableConnection


class Query(graphene.ObjectType):
    attributes = FilterConnectionField(
        AttributeCountableConnection,
        filter=AttributeFilterInput(),
        search=graphene.String(),
        sort_by=AttributeSortingInput(),
    )
    attribute = graphene.Field(
        Attribute,
        id=graphene.Argument(graphene.ID),
        slug=graphene.Argument(graphene.String),
    )

    def resolve_attributes(self, info, *args, **kwargs):
        qs = resolve_attributes(info)
        qs = filter_connection_queryset(qs, kwargs)
        return create_connection_slice(qs, info, kwargs, AttributeCountableConnection)

    def resolve_attribute(self, info, id=None, slug=None):
        return resolve_attribute(info, id, slug)


class Mutation(graphene.ObjectType):
    attribute_create = AttributeCreate.Field()
    attribute_delete = AttributeDelete.Field()
    attribute_update = AttributeUpdate.Field()
    attribute_value_create = AttributeValueCreate.Field()
    attribute_value_delete = AttributeValueDelete.Field()
    attribute_value_update = AttributeValueUpdate.Field()
