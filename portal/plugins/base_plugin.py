from copy import copy
from typing import TYPE_CHECKING, Callable, List, Optional, Union

from django.utils.functional import SimpleLazyObject
from promise.promise import Promise

from .models import PluginConfiguration

if TYPE_CHECKING:
    from ..account.models import User
    from ..channel.models import Channel
    from ..document.models import Document
    from ..entry.models import Category, Entry
    from ..session.models import Session

PluginConfigurationType = List[dict]
RequestorOrLazyObject = Union[SimpleLazyObject, "User"]


class ConfigurationTypeField:
    STRING = "String"
    MULTILINE = "Multiline"
    BOOLEAN = "Boolean"
    SECRET = "Secret"
    SECRET_MULTILINE = "SecretMultiline"
    PASSWORD = "Password"
    OUTPUT = "OUTPUT"
    CHOICES = [
        (STRING, "Field is a String"),
        (MULTILINE, "Field is a Multiline"),
        (BOOLEAN, "Field is a Boolean"),
        (SECRET, "Field is a Secret"),
        (PASSWORD, "Field is a Password"),
        (SECRET_MULTILINE, "Field is a Secret multiline"),
        (OUTPUT, "Field is a read only"),
    ]


class BasePlugin:
    PLUGIN_NAME = ""
    PLUGIN_ID = ""
    PLUGIN_DESCRIPTION = ""
    CONFIG_STRUCTURE = None
    CONFIGURATION_PER_CHANNEL = True
    DEFAULT_CONFIGURATION = []
    DEFAULT_ACTIVE = False
    HIDDEN = False

    @classmethod
    def check_plugin_id(cls, plugin_id: str) -> bool:
        """Check if given plugin_id matches with the PLUGIN_ID of this plugin."""
        return cls.PLUGIN_ID == plugin_id

    def __init__(
        self,
        *,
        configuration: PluginConfigurationType,
        active: bool,
        channel: Optional["Channel"] = None,
        requestor_getter: Optional[Callable[[], "User"]] = None,
        db_config: Optional["PluginConfiguration"] = None
    ):
        self.configuration = self.get_plugin_configuration(configuration)
        self.active = active
        self.channel = channel
        self.requestor: Optional[RequestorOrLazyObject] = (
            SimpleLazyObject(requestor_getter) if requestor_getter else requestor_getter
        )
        self.db_config = db_config

    def __str__(self):
        return self.PLUGIN_NAME

    category_created: Callable[["Category", None], None]
    category_deleted: Callable[["Category", None], None]
    category_updated: Callable[["Category", None], None]
    document_created: Callable[["Document", None], None]
    document_deleted: Callable[["Document", None], None]
    document_updated: Callable[["Document", None], None]
    entry_created: Callable[["Entry", None], None]
    entry_deleted: Callable[["Entry", None], None]
    entry_updated: Callable[["Entry", None], None]
    session_created: Callable[["Session", None], None]
    session_deleted: Callable[["Session", None], None]
    session_updated: Callable[["Session", None], None]
    consult_document: Callable[["Entry", None], None]

    @classmethod
    def _update_config_items(
        cls, configuration_to_update: List[dict], current_config: List[dict]
    ):
        config_structure: dict = (
            cls.CONFIG_STRUCTURE if cls.CONFIG_STRUCTURE is not None else {}
        )
        configuration_to_update_dict = {
            c_field["name"]: c_field.get("value") for c_field in configuration_to_update
        }
        for config_item in current_config:
            new_value = configuration_to_update_dict.get(config_item["name"])
            if new_value is None:
                continue
            item_type = config_structure.get(config_item["name"], {}).get("type")
            new_value = cls._clean_configuration_value(item_type, new_value)
            if new_value is not None:
                config_item.update([("value", new_value)])

        # Get new keys that don't exist in current_config and extend it.
        current_config_keys = set(c_field["name"] for c_field in current_config)
        missing_keys = set(configuration_to_update_dict.keys()) - current_config_keys
        for missing_key in missing_keys:
            if not config_structure.get(missing_key):
                continue
            item_type = config_structure.get(missing_key, {}).get("type")
            new_value = cls._clean_configuration_value(
                item_type, configuration_to_update_dict[missing_key]
            )
            if new_value is None:
                continue
            current_config.append(
                {
                    "name": missing_key,
                    "value": new_value,
                }
            )

    @classmethod
    def _clean_configuration_value(cls, item_type, new_value):
        """Clean the value that is saved in plugin configuration.

        Change the string provided as boolean into the bool value.
        Return None for Output type, as it's read only field.
        """
        if (
            item_type == ConfigurationTypeField.BOOLEAN
            and new_value
            and not isinstance(new_value, bool)
        ):
            new_value = new_value.lower() == "true"
        if item_type == ConfigurationTypeField.OUTPUT:
            # OUTPUT field is read only. No need to update it
            return
        return new_value

    @classmethod
    def validate_plugin_configuration(
        cls, plugin_configuration: "PluginConfiguration", **kwargs
    ):
        """Validate if provided configuration is correct.

        Raise django.core.exceptions.ValidationError otherwise.
        """
        return

    @classmethod
    def pre_save_plugin_configuration(cls, plugin_configuration: "PluginConfiguration"):
        """Trigger before plugin configuration will be saved.

        Overwrite this method if you need to trigger specific logic before saving a
        plugin configuration.
        """

    @classmethod
    def save_plugin_configuration(
        cls, plugin_configuration: "PluginConfiguration", cleaned_data
    ):
        current_config = plugin_configuration.configuration
        configuration_to_update = cleaned_data.get("configuration")
        if configuration_to_update:
            cls._update_config_items(configuration_to_update, current_config)

        if "active" in cleaned_data:
            plugin_configuration.active = cleaned_data["active"]

        cls.validate_plugin_configuration(plugin_configuration)
        cls.pre_save_plugin_configuration(plugin_configuration)
        plugin_configuration.save()

        if plugin_configuration.configuration:
            # Let's add a translated descriptions and labels
            cls._append_config_structure(plugin_configuration.configuration)

        return plugin_configuration

    @classmethod
    def _append_config_structure(cls, configuration: PluginConfigurationType):
        """Append configuration structure to config from the database.

        Database stores "key: value" pairs, the definition of fields should be declared
        inside of the plugin. Based on this, the plugin will generate a structure of
        configuration with current values and provide access to it via API.
        """
        config_structure = getattr(cls, "CONFIG_STRUCTURE") or {}
        fields_without_structure = []
        for configuration_field in configuration:

            structure_to_add = config_structure.get(configuration_field.get("name"))
            if structure_to_add:
                configuration_field.update(structure_to_add)
            else:
                fields_without_structure.append(configuration_field)

        if fields_without_structure:
            [
                configuration.remove(field)  # type: ignore
                for field in fields_without_structure
            ]

    @classmethod
    def _update_configuration_structure(cls, configuration: PluginConfigurationType):
        updated_configuration = []
        config_structure = getattr(cls, "CONFIG_STRUCTURE") or {}
        desired_config_keys = set(config_structure.keys())
        for config_field in configuration:
            if config_field["name"] not in desired_config_keys:
                continue
            updated_configuration.append(copy(config_field))

        configured_keys = set(d["name"] for d in updated_configuration)
        missing_keys = desired_config_keys - configured_keys

        if not missing_keys:
            return updated_configuration

        default_config = cls.DEFAULT_CONFIGURATION
        if not default_config:
            return updated_configuration

        update_values = [copy(k) for k in default_config if k["name"] in missing_keys]
        if update_values:
            updated_configuration.extend(update_values)
        return updated_configuration

    @classmethod
    def get_default_active(cls):
        return cls.DEFAULT_ACTIVE

    def get_plugin_configuration(
        self, configuration: PluginConfigurationType
    ) -> PluginConfigurationType:
        if not configuration:
            configuration = []
        configuration = self._update_configuration_structure(configuration)
        if configuration:
            # Let's add a translated descriptions and labels
            self._append_config_structure(configuration)
        return configuration

    def resolve_plugin_configuration(
        self, request
    ) -> Union[PluginConfigurationType, Promise[PluginConfigurationType]]:
        # Override this function to customize resolving plugin configuration in API.
        return self.configuration

    def is_event_active(self, event: str, channel=Optional[str]):
        return hasattr(self, event)
