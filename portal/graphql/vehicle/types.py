import graphene

from portal.graphql.document.dataloaders import DocumentsByVehicleIdLoader

from ...vehicle import models
from ..core.connection import CountableConnection, create_connection_slice
from ..core.fields import ConnectionField
from ..core.types import ModelObjectType
from ..document.types import DocumentCountableConnection
from .dataloaders import CategoryByIdLoader, VehiclesByCategoryIdLoader


class Vehicle(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    slug = graphene.String()
    category = graphene.Field(lambda: Category)
    document_number = graphene.String()
    is_published = graphene.Boolean()
    email = graphene.String()
    phone = graphene.String()
    address = graphene.String()
    documents = ConnectionField(DocumentCountableConnection)

    class Meta:
        model = models.Vehicle
        interfaces = [graphene.relay.Node]

    def resolve_documents(self, info, **kwargs):
        def _resolve(documents):
            return create_connection_slice(
                documents, info, kwargs, DocumentCountableConnection
            )

        return DocumentsByVehicleIdLoader(info.context).load(self.id).then(_resolve)

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
    total_vehicles = graphene.Int()

    class Meta:
        model = models.Category
        interfaces = [graphene.relay.Node]

    def resolve_vehicles(self, info, **kwargs):
        def _resolve(vehicles):
            return create_connection_slice(
                vehicles, info, kwargs, VehicleCountableConnection
            )

        return VehiclesByCategoryIdLoader(info.context).load(self.id).then(_resolve)


class CategoryCountableConnection(CountableConnection):
    class Meta:
        node = Category
