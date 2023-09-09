from collections import defaultdict
from typing import Dict, List, Tuple

from ...plugins.base_plugin import BasePlugin, ConfigurationTypeField
from .filters import filter_plugin_by_type, filter_plugin_search
from .sorters import sort_plugins
from .types import Plugin


def hide_private_configuration_fields(configuration, config_structure):
    if not config_structure:
        return

    for field in configuration:
        name = field["name"]
        value = field["value"]
        if value is None:
            continue
        field_type = config_structure.get(name, {}).get("type")
        if field_type == ConfigurationTypeField.PASSWORD:
            field["value"] = "" if value else None

        if field_type in [
            ConfigurationTypeField.SECRET,
            ConfigurationTypeField.SECRET_MULTILINE,
        ]:
            if not value:
                field["value"] = None
            elif len(value) > 4:
                field["value"] = value[-4:]
            else:
                field["value"] = value[-1:]


def aggregate_plugins_configuration(
    manager,
) -> Tuple[Dict[str, BasePlugin], Dict[str, List[BasePlugin]]]:
    global_plugins: Dict[str, BasePlugin] = {}

    for plugin in manager.all_plugins:
        hide_private_configuration_fields(plugin.configuration, plugin.CONFIG_STRUCTURE)
        if plugin.HIDDEN is True:
            continue
        global_plugins[plugin.PLUGIN_ID] = plugin
    return global_plugins


def resolve_plugin(id, manager):
    global_plugins = aggregate_plugins_configuration(manager)
    plugin: BasePlugin = manager.get_plugin(id)
    if not plugin or plugin.HIDDEN is True:
        return None

    return Plugin(
        id=plugin.PLUGIN_ID,
        global_configuration=global_plugins.get(plugin.PLUGIN_ID),
        description=plugin.PLUGIN_DESCRIPTION,
        name=plugin.PLUGIN_NAME,
    )


def resolve_plugins(manager, sort_by=None, **kwargs):
    global_plugins = aggregate_plugins_configuration(manager)
    plugin_filter = kwargs.get("filter", {})
    search_query = plugin_filter.get("search")
    filter_plugin_type = plugin_filter.get("type")

    plugins = [
        Plugin(
            id=plugin.PLUGIN_ID,
            global_configuration=plugin,
            description=plugin.PLUGIN_DESCRIPTION,
            name=plugin.PLUGIN_NAME,
        )
        for _, plugin in global_plugins.items()
    ]

    if filter_plugin_type is not None:
        plugins = filter_plugin_by_type(plugins, filter_plugin_type)
    plugins = filter_plugin_search(plugins, search_query)
    plugins = sort_plugins(plugins, sort_by)

    return plugins
