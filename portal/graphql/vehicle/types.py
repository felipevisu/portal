import graphene

from ...vehicle import models
from ..core.connection import CountableConnection, create_connection_slice
from ..core.fields import ConnectionField
from ..core.types import ModelObjectType
from ..document.types import DocumentCountableConnection
from .dataloaders import CategoryByIdLoader


class Vehicle(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    category = graphene.Field(lambda: Category)
    document_number = graphene.String()
    is_published = graphene.String()
    email = graphene.String()
    phone = graphene.String()
    address = graphene.String()
    documents = ConnectionField(DocumentCountableConnection)

    class Meta:
        model = models.Vehicle
        interfaces = [graphene.relay.Node]

    def resolve_documents(self, info, **kwargs):
        qs = self.documents.all()
        return create_connection_slice(qs, info, kwargs, DocumentCountableConnection)

    def resolve_category(self, info):
        if self.category_id:
            category_id = self.category_id
        else:
            return None
        return CategoryByIdLoader(info.context).load(category_id)


class VehicleCountableConnection(CountableConnection):
    class Meta:
        node = Vehicle


class Category(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    vehicles = ConnectionField(VehicleCountableConnection)

    class Meta:
        model = models.Category
        interfaces = [graphene.relay.Node]

    def resolve_vehicles(self, info, **kwargs):
        qs = self.vehicles.all()
        return create_connection_slice(qs, info, kwargs, VehicleCountableConnection)


class CategoryCountableConnection(CountableConnection):
    class Meta:
        node = Category
