from ..base_plugin import BasePlugin, ConfigurationTypeField


class PluginSample(BasePlugin):
    PLUGIN_ID = "plugin.sample"
    PLUGIN_NAME = "PluginSample"
    PLUGIN_DESCRIPTION = "Test plugin description"
    DEFAULT_ACTIVE = True
    CONFIGURATION_PER_CHANNEL = False
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


class ChannelPluginSample(PluginSample):
    PLUGIN_ID = "channel.plugin.sample"
    PLUGIN_NAME = "Channel Plugin"
    PLUGIN_DESCRIPTION = "Test channel plugin"
    DEFAULT_ACTIVE = True
    CONFIGURATION_PER_CHANNEL = True
    DEFAULT_CONFIGURATION = [{"name": "input-per-channel", "value": None}]
    CONFIG_STRUCTURE = {
        "input-per-channel": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Test input",
            "label": "Input per channel",
        }
    }


class InactiveChannelPluginSample(PluginSample):
    PLUGIN_ID = "channel.plugin.inactive.sample"
    PLUGIN_NAME = "Inactive Channel Plugin"
    PLUGIN_DESCRIPTION = "Test channel plugin"
    DEFAULT_ACTIVE = False
    CONFIGURATION_PER_CHANNEL = True
    DEFAULT_CONFIGURATION = [{"name": "input-per-channel", "value": None}]
    CONFIG_STRUCTURE = {
        "input-per-channel": {
            "type": ConfigurationTypeField.STRING,
            "help_text": "Test input",
            "label": "Input per channel",
        }
    }


class PluginInactive(BasePlugin):
    PLUGIN_ID = "mirumee.taxes.plugin.inactive"
    PLUGIN_NAME = "PluginInactive"
    PLUGIN_DESCRIPTION = "Test plugin description_2"
    CONFIGURATION_PER_CHANNEL = False
    DEFAULT_ACTIVE = False


class ActivePlugin(BasePlugin):
    PLUGIN_ID = "portal.x.plugin.active"
    PLUGIN_NAME = "Active"
    PLUGIN_DESCRIPTION = "Not working"
    DEFAULT_ACTIVE = True
    CONFIGURATION_PER_CHANNEL = False


ACTIVE_PLUGINS = (
    ChannelPluginSample,
    ActivePlugin,
)

INACTIVE_PLUGINS = (
    PluginInactive,
    InactiveChannelPluginSample,
)

ALL_PLUGINS = ACTIVE_PLUGINS + INACTIVE_PLUGINS
