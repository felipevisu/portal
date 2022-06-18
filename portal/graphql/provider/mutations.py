import graphene

from ...core.permissions import ProviderPermissions
from ...provider import models
from ..core.mutations import ModelBulkDeleteMutation, ModelDeleteMutation, ModelMutation
from ..core.types import NonNullList, Upload
from .types import Document, Provider, Segment


class DocumentInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    file = Upload()
    provider = graphene.ID()
    is_published = graphene.Boolean(default=False)
    publication_date = graphene.Date(required=False)
    expires = graphene.Boolean(default=False)
    begin_date = graphene.Date(required=False)
    expiration_date = graphene.Date(required=False)


class DocumentCreate(ModelMutation):
    document = graphene.Field(Document)

    class Arguments:
        input = DocumentInput(required=True)

    class Meta:
        model = models.Document
        permissions = (ProviderPermissions.MANAGE_DOCUMENTS,)


class DocumentUpdate(ModelMutation):
    document = graphene.Field(Document)

    class Arguments:
        id = graphene.ID()
        input = DocumentInput(required=True)

    class Meta:
        model = models.Document
        permissions = (ProviderPermissions.MANAGE_DOCUMENTS,)


class DocumentDelete(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Document
        permissions = (ProviderPermissions.MANAGE_DOCUMENTS,)


class ProviderInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()
    document_number = graphene.String()
    segment = graphene.ID()
    is_published = graphene.Boolean(default=False)
    publication_date = graphene.Date(required=False)


class ProviderCreate(ModelMutation):
    provider = graphene.Field(Provider)

    class Arguments:
        input = ProviderInput(required=True)

    class Meta:
        model = models.Provider
        permissions = (ProviderPermissions.MANAGE_PROVIDERS,)


class ProviderUpdate(ModelMutation):
    vehicle = graphene.Field(Provider)

    class Arguments:
        id = graphene.ID()
        input = ProviderInput(required=True)

    class Meta:
        model = models.Provider
        permissions = (ProviderPermissions.MANAGE_PROVIDERS,)


class ProviderDelete(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Provider
        permissions = (ProviderPermissions.MANAGE_PROVIDERS,)


class SegmentInput(graphene.InputObjectType):
    name = graphene.String()
    slug = graphene.String()


class SegmentCreate(ModelMutation):
    segment = graphene.Field(Segment)

    class Arguments:
        input = SegmentInput(required=True)

    class Meta:
        model = models.Segment
        permissions = (ProviderPermissions.MANAGE_SEGMENTS,)


class SegmentUpdate(ModelMutation):
    segment = graphene.Field(Segment)

    class Arguments:
        id = graphene.ID()
        input = SegmentInput(required=True)

    class Meta:
        model = models.Segment
        permissions = (ProviderPermissions.MANAGE_SEGMENTS,)


class SegmentDelete(ModelDeleteMutation):

    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Segment
        permissions = (ProviderPermissions.MANAGE_SEGMENTS,)


class SegmentBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = NonNullList(
            graphene.ID, required=True, description="List of category IDs to delete."
        )

    class Meta:
        description = "Deletes categories."
        model = models.Segment
        object_type = Segment
        permissions = (ProviderPermissions.MANAGE_SEGMENTS,)
