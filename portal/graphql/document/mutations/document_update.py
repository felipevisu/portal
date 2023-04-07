import graphene
from django.core.exceptions import ValidationError
from graphene_file_upload.scalars import Upload

from ....core.permissions import DocumentPermissions
from ....document import DocumentFileStatus, models
from ....document.events import event_document_updated
from ...core.mutations import ModelMutation
from ..types import Document
from .document_create import DocumentInput


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
        if (file or instance.default_file) and expires and not expiration_date:
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
        return DocumentUpdate(document=instance)

    @classmethod
    def post_save_action(cls, info, instance, cleaned_input):
        event_document_updated(instance.id, info.context.user)
