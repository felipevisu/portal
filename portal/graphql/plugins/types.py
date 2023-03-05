from typing import TYPE_CHECKING

import graphene

from ..channel.types import Channel
from ..core.connection import CountableConnection
from ..core.types import NonNullList
from .enums import ConfigurationTypeFieldEnum

if TYPE_CHECKING:
    from ...plugins.base_plugin import BasePlugin


class ConfigurationItem(graphene.ObjectType):
    name = graphene.String(required=True)
    value = graphene.String(required=False)
    type = graphene.Field(ConfigurationTypeFieldEnum)
    help_text = graphene.String(required=False)
    label = graphene.String(
        required=False,
    )


class PluginConfiguration(graphene.ObjectType):
    active = graphene.Boolean(required=True)
    channel = graphene.Field(Channel)
    configuration = NonNullList(ConfigurationItem)

    @staticmethod
    def resolve_configuration(root: "BasePlugin", info):
        return root.resolve_plugin_configuration(info.context)


class Plugin(graphene.ObjectType):
    id = graphene.ID(required=True)
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    global_configuration = graphene.Field(PluginConfiguration)
    channel_configurations = NonNullList(
        PluginConfiguration,
        required=True,
    )

    class Meta:
        description = "Plugin."

    @staticmethod
    def resolve_name(root: "Plugin", _info):
        return root.name

    @staticmethod
    def resolve_description(root: "Plugin", _info):
        return root.description

    @staticmethod
    def resolve_global_configuration(root: "Plugin", _info):
        return root.global_configuration

    @staticmethod
    def resolve_channel_configurations(root: "Plugin", _info):
        return root.channel_configurations or []


class PluginCountableConnection(CountableConnection):
    class Meta:
        node = Plugin
