import datetime

import graphene

from ...document import models
from ..core.connection import CountableConnection
from ..core.types import File, ModelObjectType
from ..entry.dataloaders import EntryByIdLoader


class DocumentFile(ModelObjectType):
    document = graphene.Field(lambda: Document)
    file = graphene.Field(File)
    begin_date = graphene.Date()
    expiration_date = graphene.Date()
    created = graphene.DateTime()
    updated = graphene.DateTime()

    class Meta:
        model = models.DocumentFile
        interfaces = [graphene.relay.Node]


class DocumentFileCountableConnection(CountableConnection):
    class Meta:
        node = DocumentFile


class Document(ModelObjectType):
    id = graphene.GlobalID(required=True)
    name = graphene.String(required=True)
    description = graphene.String()
    entry = graphene.Field("portal.graphql.entry.types.Entry")
    default_file = graphene.Field(lambda: DocumentFile)
    created = graphene.DateTime()
    updated = graphene.DateTime()
    publication_date = graphene.Date()
    is_published = graphene.Boolean()
    expires = graphene.Boolean()
    expired = graphene.Boolean()

    class Meta:
        model = models.Document
        interfaces = [graphene.relay.Node]

    def resolve_expired(self, info):
        if not self.expires:
            return False
        today = datetime.date.today()
        return self.default_file.expiration_date < today

    def resolve_entry(self, info):
        if self.entry_id:
            entry_id = self.entry_id
        else:
            return None
        return EntryByIdLoader(info.context).load(entry_id)


class DocumentCountableConnection(CountableConnection):
    class Meta:
        node = Document
