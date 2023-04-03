import graphene

from ....core.permissions import DocumentPermissions
from ....document import models
from ....event.events import event_document_deleted
from ...core.mutations import ModelBulkDeleteMutation, ModelDeleteMutation
from ...core.types.common import NonNullList
from ..types import Document


class DocumentDelete(ModelDeleteMutation):
    class Arguments:
        id = graphene.ID()

    class Meta:
        model = models.Document
        permissions = (DocumentPermissions.MANAGE_DOCUMENTS,)
        object_type = Document

    @classmethod
    def post_save_action(cls, info, instance):
        event_document_deleted(instance, info.context.user)


class DocumentBulkDelete(ModelBulkDeleteMutation):
    class Arguments:
        ids = NonNullList(graphene.ID, required=True)

    class Meta:
        description = "Deletes segments."
        model = models.Document
        object_type = Document
        permissions = (DocumentPermissions.MANAGE_DOCUMENTS,)
