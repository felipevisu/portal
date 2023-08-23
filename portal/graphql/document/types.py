import datetime

import graphene

from portal.graphql.channel import ChannelContext

from ...core.permissions import DocumentPermissions, EventPermissions
from ...document import models
from ..core.connection import CountableConnection
from ..core.fields import PermissionsField
from ..core.types import File, ModelObjectType
from ..core.types.common import NonNullList
from ..entry.dataloaders import EntryByIdLoader
from ..event.dataloaders import EventsByDocumentIdLoader
from ..event.types import Event
from .dataloaders import DocumentFileByIdLoader, DocumentFilesByDocumentIdLoader
from .enums import (
    DocumentFileStatusEnum,
    DocumentLoadOptionsEnum,
    DocumentLoadStatusEnum,
)


class DocumentFile(ModelObjectType):
    document = graphene.Field(lambda: Document)
    file = graphene.Field(File)
    begin_date = graphene.Date()
    expiration_date = graphene.Date()
    created = graphene.DateTime()
    updated = graphene.DateTime()
    status = DocumentFileStatusEnum()

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
    is_published = graphene.Boolean()
    expires = graphene.Boolean()
    expired = graphene.Boolean()
    files = PermissionsField(
        NonNullList(lambda: DocumentFile),
        permissions=[DocumentPermissions.MANAGE_DOCUMENTS],
    )
    events = PermissionsField(
        NonNullList(lambda: Event),
        permissions=[EventPermissions.MANAGE_EVENTS],
    )
    load_type = DocumentLoadOptionsEnum()

    class Meta:
        model = models.Document
        interfaces = [graphene.relay.Node]

    def resolve_expired(self, info):
        if self.expires and self.default_file:
            today = datetime.date.today()
            if self.default_file.expiration_date:
                return self.default_file.expiration_date < today
        return False

    def resolve_entry(self, info):
        if self.entry_id:
            entry_id = self.entry_id
        else:
            return None
        entry = EntryByIdLoader(info.context).load(entry_id)
        return entry.then(lambda entry: ChannelContext(node=entry, channel_slug=None))

    def resolve_files(self, info):
        return DocumentFilesByDocumentIdLoader(info.context).load(self.id)

    def resolve_events(self, info, **kwargs):
        def _resolve(events):
            return events[:5]

        return EventsByDocumentIdLoader(info.context).load(self.id).then(_resolve)

    def resolve_default_file(self, info, **kwargs):
        if self.default_file_id:
            return DocumentFileByIdLoader(info.context).load(self.default_file_id)


class DocumentCountableConnection(CountableConnection):
    class Meta:
        node = Document


class DocumentLoad(ModelObjectType):
    id = graphene.GlobalID(required=True)
    document = graphene.Field(Document)
    document_file = graphene.Field(DocumentFile)
    status = DocumentLoadStatusEnum()
    error_message = graphene.String()

    class Meta:
        model = models.DocumentLoad
        interfaces = [graphene.relay.Node]
