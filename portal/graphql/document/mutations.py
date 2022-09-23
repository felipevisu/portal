import graphene
from django.core.exceptions import ValidationError
from graphene_file_upload.scalars import Upload

from portal.graphql.core.types import NonNullList

from ...core.permissions import DocumentPermissions
from ...document import models
from ..core.mutations import ModelBulkDeleteMutation, ModelDeleteMutation, ModelMutation
from .types import Document


class DocumentInput(graphene.InputObjectType):
    name = graphene.String()
    description = graphene.String()
    file = Upload()
    provider = graphene.ID(required=False)
    entry = graphene.ID(required=False)
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
        object_type = Document

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        cleaned_input = super().clean_input(info, instance, data, input_cls)
        expires = data.get("expires", False)
        expiration_date = data.get("expiration_date", None)
        if expires and not expiration_date:
            message = "Este campo não pode estar vazio se o documento é expirável."
            raise ValidationError({"expiration_date": message})
        return cleaned_input


class DocumentUpdate(ModelMutation):
    document = graphene.Field(Document)

    class Arguments:
        id = graphene.ID()
        input = DocumentInput(required=True)

    class Meta:
        model = models.Document
        permissions = (DocumentPermissions.MANAGE_DOCUMENTS,)
        object_type = Document

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        cleaned_input = super().clean_input(info, instance, data, input_cls)
        expires = data.get("expires", False)
        expiration_date = data.get("expiration_date", None)
        if expires and not expiration_date:
            message = "Este campo não pode estar vazio se o documento é expirável."
            raise ValidationError({"expiration_date": message})
        if not expires:
            cleaned_input["begin_date"] = None
            cleaned_input["expiration_date"] = None
        return cleaned_input


class DocumentDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Document
        permissions = (DocumentPermissions.MANAGE_DOCUMENTS,)
        object_type = Document


class DocumentBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = NonNullList(
            graphene.ID, required=True, description="List of documents IDs to delete."
        )

    class Meta:
        description = "Deletes segments."
        model = models.Document
        object_type = Document
        permissions = (DocumentPermissions.MANAGE_DOCUMENTS,)
