import graphene
from graphene_django import DjangoObjectType

from ...document import models
from ..core.connection import ContableConnection
from .filters import DocumentFilter


class Document(DjangoObjectType):
    file_url = graphene.String()
    file_name = graphene.String()

    class Meta:
        model = models.Document
        filterset_class = DocumentFilter
        interfaces = [graphene.relay.Node]
        connection_class = ContableConnection

    def resolve_file_url(self, info):
        return self.file.url

    def resolve_file_name(self, info):
        return self.file.name.split('/')[-1]


class DocumentsConnection(graphene.Connection):
    total_count = graphene.Int()

    class Meta:
        node = Document

    def resolve_total_count(root, info, **kwargs):
        return len(root.edges)
