import graphene
from django.core.exceptions import ValidationError
from graphene_file_upload.scalars import Upload

from ....core.permissions import DocumentPermissions
from ....document import DocumentFileStatus, models
from ....document.events import event_document_created
from ...core.mutations import ModelMutation
from ..enums import DocumentLoadOptionsEnum
from ..types import Document


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
    load_type = DocumentLoadOptionsEnum()


class DocumentCreate(ModelMutation):
    document = graphene.Field(Document)

    class Arguments:
        input = DocumentInput(required=True)

    class Meta:
        model = models.Document
        object_type = Document
        permissions = (DocumentPermissions.MANAGE_DOCUMENTS,)

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

        cls.post_save_action(info, instance, cleaned_input)
        return DocumentCreate(document=instance)

    @classmethod
    def post_save_action(cls, info, instance, cleaned_input):
        event_document_created(instance.id, info.context.user)
