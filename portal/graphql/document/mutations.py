import graphene
from django.core.exceptions import ValidationError
from graphene_file_upload.scalars import Upload

from portal.core.exeptions import PermissionDenied
from portal.event.models import OneTimeToken

from ...core.permissions import DocumentPermissions
from ...document import DocumentFileStatus, models
from ...event.notifications import send_request_new_document_from_provider
from ...plugins.manager import get_plugins_manager
from ..core.mutations import (
    BaseMutation,
    ModelBulkDeleteMutation,
    ModelDeleteMutation,
    ModelMutation,
)
from ..core.types import NonNullList
from .types import Document, DocumentFile


class DocumentInput(graphene.InputObjectType):
    name = graphene.String()
    description = graphene.String()
    file = Upload(required=False)
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
        file = data.get("file", None)
        expires = data.get("expires", False)
        expiration_date = data.get("expiration_date", None)
        if file and expires and not expiration_date:
            message = "Este campo não pode estar vazio se o documento é expirável."
            raise ValidationError({"expiration_date": message})
        if not file and expires and expiration_date:
            message = "Adicione um arquivo se quiser configurar uma data de expiração"
            raise ValidationError({"file": message})
        return cleaned_input

    @classmethod
    def clean_file_input(cls, input, instance):
        file_input = {
            "file": input.pop("file", None),
            "begin_date": input.pop("begin_date", None),
            "expiration_date": input.pop("expiration_date", None),
            "status": DocumentFileStatus.APPROVED,
            "document": instance,
        }
        return {k: v for k, v in file_input.items() if v}

    @classmethod
    def perform_mutation(cls, _root, info, **data):
        input = data.get("input")
        instance = models.Document()
        cleaned_input = cls.clean_input(info, instance, input)
        file_input = cls.clean_file_input(cleaned_input, instance)
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        instance.save()

        if input.get("file", None):
            default_file = models.DocumentFile()
            default_file = cls.construct_instance(default_file, file_input)
            default_file.save()
            instance.default_file = default_file
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
        file = data.get("file", None)
        expires = data.get("expires", False)
        expiration_date = data.get("expiration_date", None)
        if file and expires and not expiration_date:
            message = "Este campo não pode estar vazio se o documento é expirável."
            raise ValidationError({"expiration_date": message})
        if not file and not instance.default_file and expires and expiration_date:
            message = "Adicione um arquivo se quiser configurar uma data de expiração"
            raise ValidationError({"file": message})
        return cleaned_input

    @classmethod
    def clean_file_input(cls, input, instance):
        file_input = {
            "file": input.pop("file", None),
            "begin_date": input.pop("begin_date", None),
            "expiration_date": input.pop("expiration_date", None),
            "status": DocumentFileStatus.APPROVED,
            "document": instance,
        }
        return {k: v for k, v in file_input.items() if v}

    @classmethod
    def get_default_file(cls, instance, input):
        if "file" in input and (instance.expires or instance.default_file is None):
            return models.DocumentFile()
        return instance.default_file

    @classmethod
    def save_default_file(cls, instance, input):
        default_file = cls.get_default_file(instance, input)
        if default_file:
            default_file = cls.construct_instance(default_file, input)
            default_file.save()
            instance.default_file = default_file
            instance.save(update_fields=["default_file"])

    @classmethod
    def perform_mutation(cls, _root, info, id, input):
        instance = cls.get_node_or_error(info, id, only_type=Document)
        cleaned_input = cls.clean_input(info, instance, input)
        file_input = cls.clean_file_input(cleaned_input, instance)
        instance = cls.construct_instance(instance, cleaned_input)
        cls.clean_instance(info, instance)
        instance.save()
        cls.save_default_file(instance, file_input)
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


class RequestNewDocument(BaseMutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.ID(required=True)

    class Meta:
        permissions = (DocumentPermissions.MANAGE_DOCUMENTS,)

    @classmethod
    def perform_mutation(cls, _root, info, id):
        document = cls.get_node_or_error(info, id, only_type=Document)
        manager = get_plugins_manager()
        send_request_new_document_from_provider(document, manager)
        return RequestNewDocument(success=True)


class ValidateDocumentToken(BaseMutation):
    success = graphene.Boolean()

    class Arguments:
        token = graphene.String(required=True)

    @classmethod
    def perform_mutation(cls, _root, info, token):
        token = OneTimeToken.objects.filter(token=token).first()
        success = False
        if token:
            success = True
        return RequestNewDocument(success=success)


class ApproveDocumentFile(BaseMutation):
    document_file = graphene.Field(DocumentFile)

    class Arguments:
        id = graphene.ID(required=True)

    @classmethod
    def perform_mutation(cls, _root, info, id):
        document_file = cls.get_node_or_error(info, id, only_type=DocumentFile)
        document_file.status = DocumentFileStatus.APPROVED
        document_file.save(update_fields=["status", "updated"])
        document = document_file.document
        document.default_document = document_file
        document.save(update_fields=["document_file", "updated"])
        return ApproveDocumentFile(document_file=document_file)


class RefuseDocumentFile(BaseMutation):
    document_file = graphene.Field(DocumentFile)

    class Arguments:
        id = graphene.ID(required=True)

    @classmethod
    def perform_mutation(cls, _root, info, id):
        document_file = cls.get_node_or_error(info, id, only_type=DocumentFile)
        document_file.status = DocumentFileStatus.REFUSED
        document_file.save(update_fields=["status", "updated"])
        return RefuseDocumentFile(document_file=document_file)


class RestoreDocumentFile(BaseMutation):
    document_file = graphene.Field(DocumentFile)

    class Arguments:
        id = graphene.ID(required=True)

    @classmethod
    def perform_mutation(cls, _root, info, id):
        document_file = cls.get_node_or_error(info, id, only_type=DocumentFile)
        document = document_file.document
        document.default_file = document_file
        document.save(update_fields=["default_file", "updated"])
        return RestoreDocumentFile(document_file=document_file)


class DocumentFileDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID()

    @classmethod
    def clean_instance(cls, info, instance):
        document = instance.document
        if document.default_file == instance:
            raise ValidationError(
                {"id": "Não é possível excluir o arquivo principal do documento"}
            )

    class Meta:
        model = models.DocumentFile
        permissions = (DocumentPermissions.MANAGE_DOCUMENTS,)
        object_type = DocumentFile

    @classmethod
    def perform_mutation(cls, root, info, **data):
        if not cls.check_permissions(info.context):
            return PermissionDenied()

        node_id = data.get("id")
        model_type = cls.get_type_for_model()
        instance = cls.get_node_or_error(info, node_id, only_type=model_type)
        cls.clean_instance(info, instance)

        if instance:
            db_id = instance.id
            instance.delete()
            instance.id = db_id

        return cls.success_response(instance)
