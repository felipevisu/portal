import datetime

import graphene

from ...document import models
from ..core.connection import CountableConnection
from ..core.types import File, ModelObjectType
from ..provider.dataloaders import ProviderByIdLoader
from ..vehicle.dataloaders import VehicleByIdLoader


class Document(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    description = graphene.String()
    vehicle = graphene.Field("portal.graphql.vehicle.types.Vehicle")
    provider = graphene.Field("portal.graphql.provider.types.Provider")
    created = graphene.DateTime()
    updated = graphene.DateTime()
    begin_date = graphene.Date()
    publication_date = graphene.Date()
    expiration_date = graphene.Date()
    is_published = graphene.Boolean()
    expires = graphene.Boolean()
    file = graphene.Field(File)
    expired = graphene.Boolean()

    class Meta:
        model = models.Document
        interfaces = [graphene.relay.Node]

    def resolve_expired(self, info):
        if not self.expires:
            return False
        today = datetime.date.today()
        return self.expiration_date < today

    def resolve_vehicle(self, info):
        if self.vehicle_id:
            vehicle_id = self.vehicle_id
        else:
            return None
        return VehicleByIdLoader(info.context).load(vehicle_id)

    def resolve_provider(self, info):
        if self.provider_id:
            provider_id = self.provider_id
        else:
            return None
        return ProviderByIdLoader(info.context).load(provider_id)


class DocumentCountableConnection(CountableConnection):
    class Meta:
        node = Document
