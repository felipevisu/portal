import graphene

from ....entry.tasks import consult_document
from ....plugins.manager import get_plugins_manager
from ...core.mutations import (
    BaseMutation,
)
from ..types import Entry


class ConsultDocument(BaseMutation):
    entry = graphene.Field(Entry)

    class Arguments:
        id = graphene.ID(required=True)

    @classmethod
    def perform_mutation(cls, _root, info, id):
        entry = cls.get_node_or_error(info, id, only_type=Entry)
        manager = get_plugins_manager()
        user = info.context.user
        consult_document(entry, manager, user)
        return ConsultDocument(entry=entry)
