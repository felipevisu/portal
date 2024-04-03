import graphene
from django.core.exceptions import ValidationError

from ....core.exceptions import PermissionDenied
from ....core.permissions import DocumentPermissions
from ....document import (
    DocumentFileStatus,
    DocumentLoadOptions,
    DocumentLoadStatus,
    models,
)
from ....document.events import event_document_approved, event_document_declined
from ....document.notifications import (
    send_new_document_received,
    send_request_new_document,
)
from ....document.tasks import load_new_document_from_api
from ....event.models import OneTimeToken
from ....plugins.manager import get_plugins_manager
from ...core.mutations import BaseMutation, ModelDeleteMutation, ModelMutation
from ...core.types.upload import Upload
from ..types import Document, DocumentFile, DocumentLoad


class RequestNewDocument(BaseMutation):
    class Arguments:
        id = graphene.ID(required=True)

    class Meta:
        permissions = (DocumentPermissions.MANAGE_DOCUMENTS,)

    @classmethod
    def perform_mutation(cls, _root, info, id):
        document = cls.get_node_or_error(info, id, only_type=Document)
        manager = get_plugins_manager()
        user = info.context.user
        send_request_new_document(document, manager, user)
        return RequestNewDocument()


class LoadNewDocumentFromAPI(BaseMutation):
    document_load = graphene.Field(DocumentLoad)

    class Arguments:
        id = graphene.ID(required=True)

    class Meta:
        permissions = (DocumentPermissions.MANAGE_DOCUMENTS,)

    @classmethod
    def clean_instance(cls, info, instance):
        if instance.load_type == DocumentLoadOptions.EMPTY:
            raise ValidationError(
                {"load_type": "O documento precisa ter um tipo de consulta definido."}
            )

    @classmethod
    def perform_mutation(cls, _root, info, id):
        document = cls.get_node_or_error(info, id, only_type=Document)
        cls.clean_instance(info, document)
        document_load = load_new_document_from_api(
            document_id=document.id, user_id=info.context.user.id
        )
        return LoadNewDocumentFromAPI(document_load=document_load)


class TokenMixin:
    @classmethod
    def clean_token(cls, token):
        if not token:
            raise ValidationError("Token expirado")
        document = token.document
        if not document:
            raise ValidationError("Documento não existe mais")


class ValidateDocumentToken(TokenMixin, BaseMutation):
    document = graphene.Field(Document)

    class Arguments:
        token = graphene.String(required=True)

    @classmethod
    def perform_mutation(cls, _root, info, token):
        token = OneTimeToken.objects.filter(token=token).first()
        cls.clean_token(token)
        return ValidateDocumentToken(document=token.document)


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
        document.default_file = document_file
        document.save(update_fields=["default_file", "updated"])
        cls.post_save_action(info, document)
        return ApproveDocumentFile(document_file=document_file)

    @classmethod
    def post_save_action(cls, info, instance):
        event_document_approved(instance.id, info.context.user.id)


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

    @classmethod
    def post_save_action(cls, info, instance):
        event_document_declined(instance.id, info.context.user.id)


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


class DocumentUpdateByEntryInput(graphene.InputObjectType):
    file = Upload()
    begin_date = graphene.Date()
    expiration_date = graphene.Date()


class DocumentUpdateByEntry(TokenMixin, ModelMutation):
    class Arguments:
        token = graphene.String()
        input = DocumentUpdateByEntryInput()

    class Meta:
        model = models.DocumentFile
        object_type = DocumentFile

    @classmethod
    def clean_input(cls, info, instance, data, input_cls=None):
        cleaned_input = super().clean_input(info, instance, data, input_cls)
        if instance.document.expires:
            begin_date = data.get("begin_date", None)
            if not begin_date:
                message = "Este campo não pode estar vazio"
                raise ValidationError({"begin_date": message})
            expiration_date = data.get("expiration_date", None)
            if not expiration_date:
                message = "Este campo não pode estar vazio"
                raise ValidationError({"expiration_date": message})
        file = data.get("file", None)
        if not file:
            message = "Você precisa adicionar um aquivo para enviar."
            raise ValidationError({"file": message})
        return cleaned_input

    @classmethod
    def perform_mutation(cls, root, info, token, **data):
        token = OneTimeToken.objects.filter(token=token).first()
        cls.clean_token(token)
        input = data.get("input")
        instance = models.DocumentFile(document=token.document)
        cleaned_input = cls.clean_input(info, instance, input)
        instance = cls.construct_instance(instance, cleaned_input)
        instance.status = DocumentFileStatus.WAITING
        instance.save()
        token.delete()
        cls.post_save_action(info, instance, cleaned_input)
        return DocumentUpdateByEntry()

    @classmethod
    def post_save_action(cls, info, instance, cleaned_input):
        manager = get_plugins_manager()
        send_new_document_received(instance.document, manager)
