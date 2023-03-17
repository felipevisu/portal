import graphene

from ..core.connection import create_connection_slice
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
from .resolvers import resolve_attributes
from .sorters import AttributeSortingInput
from .types import AttributeCountableConnection


class Query(graphene.ObjectType):
    attributes = FilterConnectionField(
        AttributeCountableConnection,
        filter=AttributeFilterInput(),
        search=graphene.String(),
        sort_by=AttributeSortingInput(),
    )

    def resolve_attributes(self, info, *, search=None, **kwargs):
        qs = resolve_attributes(info)
        return create_connection_slice(qs, info, kwargs, AttributeCountableConnection)


class Mutation(graphene.ObjectType):
    attribute_create = AttributeCreate.Field()
    attribute_delete = AttributeDelete.Field()
    attribute_update = AttributeUpdate.Field()
    attribute_value_create = AttributeValueCreate.Field()
    attribute_value_delete = AttributeValueDelete.Field()
    attribute_value_update = AttributeValueUpdate.Field()
