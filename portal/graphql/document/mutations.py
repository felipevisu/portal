import graphene
from django.core.exceptions import ValidationError
from graphene_file_upload.scalars import Upload

from ...core.permissions import DocumentPermissions
from ...document import models
from ..core.mutations import ModelBulkDeleteMutation, ModelDeleteMutation, ModelMutation
from ..core.types import NonNullList
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

    @classmethod
    def default_input(cls, input):
        default_input = {
            "file": input.pop("file"),
            "begin_date": input.pop("begin_date", None),
            "expiration_date": input.pop("expiration_date", None),
        }
        return default_input

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        input = data.get("input")
        instance = models.Document()
        cleaned_input = cls.clean_input(info, instance, input)
        default_input = cls.default_input(cleaned_input)
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        instance.save()
        default_file = models.DocumentFile()
        default_file = cls.construct_instance(default_file, default_input)
        default_file.document = instance
        instance.default_file = default_file
        default_file.save()
        instance.save(update_fields=["default_file"])

        return DocumentCreate(document=instance)


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

    @classmethod
    def default_input(cls, input):
        default_input = {
            "file": input.pop("file", None),
            "begin_date": input.pop("begin_date", None),
            "expiration_date": input.pop("expiration_date", None),
        }
        return default_input

    @classmethod
    def save_default_file(cls, instance, input):
        if input["file"] and instance.expires:
            default_file = models.DocumentFile()
            default_file = cls.construct_instance(default_file, input)
            default_file.document = instance
            default_file.save()
            instance.default_file = default_file
            instance.save(update_fields=["default_file"])
        else:
            input.pop("file")
            default_file = cls.construct_instance(instance.default_file, input)
            default_file.save()

    @classmethod
    def perform_mutation(cls, _root, info, id, input):
        instance = cls.get_node_or_error(info, id, only_type=Document)
        cleaned_input = cls.clean_input(info, instance, input)
        default_input = cls.default_input(cleaned_input)
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        instance.save()
        cls.save_default_file(instance, default_input)
        return DocumentCreate(document=instance)


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
