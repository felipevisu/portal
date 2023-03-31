from collections import defaultdict
from typing import TYPE_CHECKING, Any, Callable, DefaultDict, Dict, List, Optional, Type

import opentracing
from django.conf import settings
from django.utils.module_loading import import_string

from ..channel.models import Channel
from .models import PluginConfiguration

if TYPE_CHECKING:
    from ..account.models import User
    from ..entry.models import Category, Entry
    from .base_plugin import BasePlugin


class PluginsManager:
    """Base manager for handling plugins logic."""

    plugins_per_channel: Dict[str, List["BasePlugin"]] = {}
    global_plugins: List["BasePlugin"] = []
    channel: Optional["Channel"] = (None,)
    all_plugins: List["BasePlugin"] = []

    def _load_plugin(
        self,
        PluginClass: Type["BasePlugin"],
        db_configs_map: dict,
        channel: Optional["Channel"] = None,
        requestor_getter=None,
    ) -> "BasePlugin":
        db_config = None
        if PluginClass.PLUGIN_ID in db_configs_map:
            db_config = db_configs_map[PluginClass.PLUGIN_ID]
            plugin_config = db_config.configuration
            active = db_config.active
            channel = db_config.channel
        else:
            plugin_config = PluginClass.DEFAULT_CONFIGURATION
            active = PluginClass.get_default_active()

        return PluginClass(
            configuration=plugin_config,
            active=active,
            channel=channel,
            requestor_getter=requestor_getter,
            db_config=db_config,
        )

    def __init__(self, plugins: List[str], requestor_getter=None):
        with opentracing.global_tracer().start_active_span("PluginsManager.__init__"):
            self.all_plugins = []
            self.global_plugins = []
            self.plugins_per_channel = defaultdict(list)

            global_db_configs, channel_db_configs = self._get_db_plugin_configs()
            channels = Channel.objects.all()

            for plugin_path in plugins:
                with opentracing.global_tracer().start_active_span(f"{plugin_path}"):
                    PluginClass = import_string(plugin_path)
                    if not getattr(PluginClass, "CONFIGURATION_PER_CHANNEL", False):
                        plugin = self._load_plugin(
                            PluginClass,
                            global_db_configs,
                            requestor_getter=requestor_getter,
                        )
                        self.global_plugins.append(plugin)
                        self.all_plugins.append(plugin)
                    else:
                        for channel in channels:
                            channel_configs = channel_db_configs.get(channel, {})
                            plugin = self._load_plugin(
                                PluginClass, channel_configs, channel, requestor_getter
                            )
                            self.plugins_per_channel[channel.slug].append(plugin)
                            self.all_plugins.append(plugin)

            for channel in channels:
                self.plugins_per_channel[channel.slug].extend(self.global_plugins)

    def _get_db_plugin_configs(self):
        with opentracing.global_tracer().start_active_span("_get_db_plugin_configs"):
            qs = (
                PluginConfiguration.objects.all()
                .using(settings.DATABASE_CONNECTION_REPLICA_NAME)
                .prefetch_related("channel")
            )
            channel_configs: DefaultDict[Channel, Dict] = defaultdict(dict)
            global_configs = {}
            for db_plugin_config in qs:
                channel = db_plugin_config.channel
                if channel is None:
                    global_configs[db_plugin_config.identifier] = db_plugin_config
                else:
                    channel_configs[channel][
                        db_plugin_config.identifier
                    ] = db_plugin_config
            return global_configs, channel_configs

    def __run_method_on_plugins(
        self,
        method_name: str,
        default_value: Any,
        *args,
        channel_slug: Optional[str] = None,
        **kwargs,
    ):
        """Try to run a method with the given name on each declared active plugin."""
        value = default_value
        plugins = self.get_plugins(channel_slug=channel_slug, active_only=True)
        for plugin in plugins:
            value = self.__run_method_on_single_plugin(
                plugin, method_name, value, *args, **kwargs
            )
        return value

    def __run_method_on_single_plugin(
        self,
        plugin: Optional["BasePlugin"],
        method_name: str,
        previous_value: Any,
        *args,
        **kwargs,
    ) -> Any:
        """Run method_name on plugin.

        Method will return value returned from plugin's
        method. If plugin doesn't have own implementation of expected method_name, it
        will return previous_value.
        """
        plugin_method = getattr(plugin, method_name, NotImplemented)
        if plugin_method == NotImplemented:
            return previous_value
        returned_value = plugin_method(
            *args, **kwargs, previous_value=previous_value
        )  # type:ignore
        if returned_value == NotImplemented:
            return previous_value
        return returned_value

    def __run_plugin_method_until_first_success(
        self,
        method_name: str,
        default_value,
        *args,
    ):
        plugins = self.get_plugins()
        for plugin in plugins:
            result = self.__run_method_on_single_plugin(
                plugin, method_name, default_value, *args
            )
            if result is not None:
                return result
        return None

    def category_created(self, category: "Category"):
        default_value = None
        return self.__run_method_on_plugins("category_created", default_value, category)

    def category_updated(self, category: "Category"):
        default_value = None
        return self.__run_method_on_plugins("category_updated", default_value, category)

    def category_deleted(self, category: "Category"):
        default_value = None
        return self.__run_method_on_plugins("category_deleted", default_value, category)

    def consult_document(self, entry: "Entry"):
        default_value = None
        return self.__run_plugin_method_until_first_success(
            "consult_document", default_value, entry
        )

    def get_plugins(
        self, channel_slug: Optional[str] = None, active_only=False
    ) -> List["BasePlugin"]:
        """Return list of plugins for a given channel."""
        if channel_slug:
            plugins = self.plugins_per_channel[channel_slug]
        else:
            plugins = self.all_plugins

        if active_only:
            plugins = [plugin for plugin in plugins if plugin.active]
        return plugins

    def notify(
        self,
        event: str,
        payload: dict,
        channel_slug: Optional[str] = None,
        plugin_id: Optional[str] = None,
    ):
        default_value = None
        if plugin_id:
            plugin = self.get_plugin(plugin_id, channel_slug=channel_slug)
            return self.__run_method_on_single_plugin(
                plugin=plugin,
                method_name="notify",
                previous_value=default_value,
                event=event,
                payload=payload,
            )
        return self.__run_method_on_plugins(
            "notify", default_value, event, payload, channel_slug=channel_slug
        )

    def _get_all_plugin_configs(self):
        with opentracing.global_tracer().start_active_span("_get_all_plugin_configs"):
            if not hasattr(self, "_plugin_configs"):
                plugin_configurations = PluginConfiguration.objects.prefetch_related(
                    "channel"
                ).all()
                self._plugin_configs_per_channel: DefaultDict[
                    Channel, Dict
                ] = defaultdict(dict)
                self._global_plugin_configs = {}
                for pc in plugin_configurations:
                    channel = pc.channel
                    if channel is None:
                        self._global_plugin_configs[pc.identifier] = pc
                    else:
                        self._plugin_configs_per_channel[channel][pc.identifier] = pc
            return self._global_plugin_configs, self._plugin_configs_per_channel

    def save_plugin_configuration(
        self, plugin_id, channel_slug: Optional[str], cleaned_data: dict
    ):
        if channel_slug:
            plugins = self.get_plugins(channel_slug=channel_slug)
            channel = Channel.objects.filter(slug=channel_slug).first()
            if not channel:
                return None
        else:
            channel = None
            plugins = self.global_plugins

        for plugin in plugins:
            if plugin.PLUGIN_ID == plugin_id:
                plugin_configuration, _ = PluginConfiguration.objects.get_or_create(
                    identifier=plugin_id,
                    channel=channel,
                    defaults={"configuration": plugin.configuration},
                )
                configuration = plugin.save_plugin_configuration(
                    plugin_configuration, cleaned_data
                )
                configuration.name = plugin.PLUGIN_NAME
                configuration.description = plugin.PLUGIN_DESCRIPTION
                plugin.active = configuration.active
                plugin.configuration = configuration.configuration
                return configuration

    def get_plugin(
        self, plugin_id: str, channel_slug: Optional[str] = None
    ) -> Optional["BasePlugin"]:
        plugins = self.get_plugins(channel_slug=channel_slug)
        for plugin in plugins:
            if plugin.check_plugin_id(plugin_id):
                return plugin
        return None

    def is_event_active_for_any_plugin(
        self, event: str, channel_slug: Optional[str] = None
    ) -> bool:
        """Check if any plugin supports defined event."""
        plugins = (
            self.plugins_per_channel[channel_slug] if channel_slug else self.all_plugins
        )
        only_active_plugins = [plugin for plugin in plugins if plugin.active]
        return any([plugin.is_event_active(event) for plugin in only_active_plugins])


def get_plugins_manager(
    requestor_getter: Optional[Callable[[], "User"]] = None
) -> PluginsManager:
    with opentracing.global_tracer().start_active_span("get_plugins_manager"):
        return PluginsManager(settings.PLUGINS, requestor_getter)
