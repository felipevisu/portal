import graphene

from ....entry import models
from ...core.connection import CountableConnection
from ...core.types import ModelObjectType


class Category(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    total_entries = graphene.Int()

    class Meta:
        model = models.Category
        interfaces = [graphene.relay.Node]

    def resolve_total_entries(self, info, **kwargs):
        return self.entries.count()


class CategoryCountableConnection(CountableConnection):
    class Meta:
        node = Category
