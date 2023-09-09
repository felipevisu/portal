from typing import TYPE_CHECKING, Any, Callable, List, Optional, Type

from django.conf import settings
from django.utils.module_loading import import_string

from .models import PluginConfiguration

if TYPE_CHECKING:
    from ..account.models import User
    from ..entry.models import Category, Entry
    from .base_plugin import BasePlugin


class PluginsManager:
    """Base manager for handling plugins logic."""

    global_plugins: List["BasePlugin"] = []
    all_plugins: List["BasePlugin"] = []

    def _load_plugin(
        self,
        PluginClass: Type["BasePlugin"],
        db_configs_map: dict,
        requestor_getter=None,
    ) -> "BasePlugin":
        db_config = None
        if PluginClass.PLUGIN_ID in db_configs_map:
            db_config = db_configs_map[PluginClass.PLUGIN_ID]
            plugin_config = db_config.configuration
            active = db_config.active
        else:
            plugin_config = PluginClass.DEFAULT_CONFIGURATION
            active = PluginClass.get_default_active()

        return PluginClass(
            configuration=plugin_config,
            active=active,
            requestor_getter=requestor_getter,
            db_config=db_config,
        )

    def __init__(self, plugins: List[str], requestor_getter=None):
        self.all_plugins = []
        self.global_plugins = []

        global_db_configs = self._get_db_plugin_configs()

        for plugin_path in plugins:
            PluginClass = import_string(plugin_path)
            plugin = self._load_plugin(
                PluginClass,
                global_db_configs,
                requestor_getter=requestor_getter,
            )
            self.global_plugins.append(plugin)
            self.all_plugins.append(plugin)

    def _get_db_plugin_configs(self):
        qs = PluginConfiguration.objects.all().using(
            settings.DATABASE_CONNECTION_REPLICA_NAME
        )
        global_configs = {}
        for db_plugin_config in qs:
            global_configs[db_plugin_config.identifier] = db_plugin_config
        return global_configs

    def __run_method_on_plugins(
        self,
        method_name: str,
        default_value: Any,
        *args,
        **kwargs,
    ):
        """Try to run a method with the given name on each declared active plugin."""
        value = default_value
        plugins = self.get_plugins(active_only=True)
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

    def get_plugins(self, active_only=False) -> List["BasePlugin"]:
        plugins = self.all_plugins

        if active_only:
            plugins = [plugin for plugin in plugins if plugin.active]
        return plugins

    def notify(
        self,
        event: str,
        payload: dict,
        plugin_id: Optional[str] = None,
    ):
        default_value = None
        if plugin_id:
            plugin = self.get_plugin(plugin_id)
            return self.__run_method_on_single_plugin(
                plugin=plugin,
                method_name="notify",
                previous_value=default_value,
                event=event,
                payload=payload,
            )
        return self.__run_method_on_plugins("notify", default_value, event, payload)

    def consult(
        self,
        document: dict,
        plugin_id: Optional[str] = None,
    ):
        default_value = None
        if plugin_id:
            plugin = self.get_plugin(plugin_id)
            return self.__run_method_on_single_plugin(
                plugin=plugin,
                method_name="consult",
                previous_value=default_value,
                document=document,
            )
        return self.__run_plugin_method_until_first_success(
            "consult", default_value, document
        )

    def _get_all_plugin_configs(self):
        if not hasattr(self, "_plugin_configs"):
            plugin_configurations = PluginConfiguration.objects.all()
            self._global_plugin_configs = {}
            for pc in plugin_configurations:
                self._global_plugin_configs[pc.identifier] = pc
        return self._global_plugin_configs

    def save_plugin_configuration(self, plugin_id, cleaned_data: dict):
        plugins = self.global_plugins

        for plugin in plugins:
            if plugin.PLUGIN_ID == plugin_id:
                plugin_configuration, _ = PluginConfiguration.objects.get_or_create(
                    identifier=plugin_id,
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

    def get_plugin(self, plugin_id: str) -> Optional["BasePlugin"]:
        plugins = self.get_plugins()
        for plugin in plugins:
            if plugin.check_plugin_id(plugin_id):
                return plugin
        return None

    def is_event_active_for_any_plugin(self, event: str) -> bool:
        """Check if any plugin supports defined event."""
        plugins = self.all_plugins
        only_active_plugins = [plugin for plugin in plugins if plugin.active]
        return any([plugin.is_event_active(event) for plugin in only_active_plugins])


def get_plugins_manager(
    requestor_getter: Optional[Callable[[], "User"]] = None
) -> PluginsManager:
    return PluginsManager(settings.PLUGINS, requestor_getter)
