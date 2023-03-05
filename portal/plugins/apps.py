from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string


class PluginConfig(AppConfig):
    name = "portal.plugins"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        plugins = getattr(settings, "PLUGINS", [])

        for plugin_path in plugins:
            self.load_and_check_plugin(plugin_path)

    def load_and_check_plugin(self, plugin_path: str):
        try:
            plugin = import_string(plugin_path)
        except ImportError as e:
            raise (ImportError(f"Failed to import plugin {plugin_path}: {e}"))

        self.check_plugin_fields(["PLUGIN_ID"], plugin)

    def check_plugin_fields(self, fields, plugin_class):
        name = plugin_class.__name__  # type: ignore

        for field in fields:
            if not getattr(plugin_class, field, None):
                raise ImproperlyConfigured(f"Missing field {field} for plugin - {name}")
