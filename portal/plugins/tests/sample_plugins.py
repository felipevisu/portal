from ..base_plugin import BasePlugin, ConfigurationTypeField


class PluginSample(BasePlugin):
    PLUGIN_ID = "plugin.sample"
    PLUGIN_NAME = "PluginSample"
    PLUGIN_DESCRIPTION = "Test plugin description"
    DEFAULT_ACTIVE = True
    DEFAULT_CONFIGURATION = [
        {"name": "Username", "value": "admin"},
        {"name": "Password", "value": None},
        {"name": "Use sandbox", "value": False},
        {"name": "API private key", "value": None},
    ]

    CONFIG_STRUCTURE = {
        "Username": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Username input field",
            "label": "Username",
        },
        "Password": {
            "type": ConfigurationTypeField.PASSWORD,
            "help_text": "Password input field",
            "label": "Password",
        },
        "Use sandbox": {
            "type": ConfigurationTypeField.BOOLEAN,
            "help_text": "Use sandbox",
            "label": "Use sandbox",
        },
        "API private key": {
            "type": ConfigurationTypeField.SECRET,
            "help_text": "API key",
            "label": "Private key",
        },
        "certificate": {
            "type": ConfigurationTypeField.SECRET_MULTILINE,
            "help_text": "",
            "label": "Multiline certificate",
        },
    }


class PluginInactive(BasePlugin):
    PLUGIN_ID = "mirumee.taxes.plugin.inactive"
    PLUGIN_NAME = "PluginInactive"
    PLUGIN_DESCRIPTION = "Test plugin description_2"
    DEFAULT_ACTIVE = False


class ActivePlugin(BasePlugin):
    PLUGIN_ID = "portal.x.plugin.active"
    PLUGIN_NAME = "Active"
    PLUGIN_DESCRIPTION = "Not working"
    DEFAULT_ACTIVE = True


ACTIVE_PLUGINS = (ActivePlugin,)

INACTIVE_PLUGINS = (PluginInactive,)

ALL_PLUGINS = ACTIVE_PLUGINS + INACTIVE_PLUGINS
