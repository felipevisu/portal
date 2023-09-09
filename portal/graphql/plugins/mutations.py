import graphene
from django.core.exceptions import ValidationError

from ...core.permissions import PluginsPermissions
from ...plugins.manager import get_plugins_manager
from ..core.mutations import BaseMutation
from ..core.types import NonNullList
from .dataloaders import get_plugin_manager_promise
from .resolvers import resolve_plugin
from .types import Plugin


class ConfigurationItemInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    value = graphene.String(required=False)


class PluginUpdateInput(graphene.InputObjectType):
    active = graphene.Boolean(required=False)
    configuration = NonNullList(ConfigurationItemInput, required=False)


class PluginUpdate(BaseMutation):
    plugin = graphene.Field(Plugin)

    class Arguments:
        id = graphene.ID(required=True)
        input = PluginUpdateInput(
            required=True,
        )

    class Meta:
        permissions = (PluginsPermissions.MANAGE_PLUGINS,)

    @classmethod
    def clean_input(cls, info, data):
        plugin_id = data.get("id")
        input_data = data.get("input")

        manager = get_plugin_manager_promise(info.context).get()
        plugin = manager.get_plugin(plugin_id)
        if not plugin or plugin.HIDDEN is True:
            raise ValidationError({"id": ValidationError("Plugin doesn't exist.")})
        return {"plugin": plugin, "data": input_data}

    @classmethod
    def perform_mutation(cls, _root, info, /, **data):
        cleaned_data = cls.clean_input(info, data)
        plugin_id = cleaned_data["plugin"].PLUGIN_ID
        input_data = cleaned_data["data"]
        manager = get_plugin_manager_promise(info.context).get()
        manager.save_plugin_configuration(plugin_id, input_data)
        manager = get_plugins_manager()
        return PluginUpdate(plugin=resolve_plugin(plugin_id, manager))
