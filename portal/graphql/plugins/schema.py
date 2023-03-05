import graphene

from ...core.permissions import PluginsPermissions
from ..core.connection import create_connection_slice
from ..core.fields import ConnectionField
from ..core.tracing import traced_resolver
from .dataloaders import plugin_manager_promise_callback
from .filters import PluginFilterInput
from .mutations import PluginUpdate
from .resolvers import resolve_plugin, resolve_plugins
from .sorters import PluginSortingInput
from .types import Plugin, PluginCountableConnection


class Query(graphene.ObjectType):
    plugin = graphene.Field(Plugin, id=graphene.Argument(graphene.ID, required=True))
    plugins = ConnectionField(
        PluginCountableConnection,
        filter=PluginFilterInput(),
        sort_by=PluginSortingInput(),
    )

    @staticmethod
    @traced_resolver
    @plugin_manager_promise_callback
    def resolve_plugin(_root, _info, manager, **data):
        return resolve_plugin(data.get("id"), manager)

    @staticmethod
    @traced_resolver
    @plugin_manager_promise_callback
    def resolve_plugins(_root, info, manager, **kwargs):
        qs = resolve_plugins(manager, **kwargs)
        return create_connection_slice(qs, info, kwargs, PluginCountableConnection)


class Mutation(graphene.ObjectType):
    plugin_update = PluginUpdate.Field()
