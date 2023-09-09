import copy

import pytest

from ..base_plugin import ConfigurationTypeField
from ..manager import PluginsManager
from ..models import PluginConfiguration
from .sample_plugins import ALL_PLUGINS, PluginInactive, PluginSample


@pytest.fixture
def plugin_configuration():
    configuration, _ = PluginConfiguration.objects.get_or_create(
        identifier=PluginSample.PLUGIN_ID,
        name=PluginSample.PLUGIN_NAME,
        defaults={
            "active": PluginSample.DEFAULT_ACTIVE,
            "configuration": PluginSample.DEFAULT_CONFIGURATION,
            "name": PluginSample.PLUGIN_NAME,
        },
    )
    configuration.refresh_from_db()
    return configuration


@pytest.fixture
def email_configuration():
    return {
        "use_tls": False,
        "use_ssl": False,
        "host": "localhost",
        "port": 1025,
        "username": "test",
        "password": "test",
        "sender_name": "test_name",
        "sender_address": "test_address",
    }


@pytest.fixture
def inactive_plugin_configuration():
    return PluginConfiguration.objects.get_or_create(
        identifier=PluginInactive.PLUGIN_ID,
        name=PluginInactive.PLUGIN_NAME,
        defaults={
            "active": PluginInactive.DEFAULT_ACTIVE,
            "configuration": PluginInactive.DEFAULT_CONFIGURATION,
            "name": PluginInactive.PLUGIN_NAME,
        },
    )[0]


@pytest.fixture
def new_config():
    return {"name": "Foo", "value": "bar"}


@pytest.fixture
def new_config_structure():
    return {"type": ConfigurationTypeField.STRING, "help_text": "foo", "label": "foo"}


@pytest.fixture
def plugins_manager():
    return PluginsManager(plugins=[])


@pytest.fixture
def all_plugins_manager():
    plugins_as_module_paths = [p.__module__ + "." + p.__name__ for p in ALL_PLUGINS]
    return PluginsManager(plugins=plugins_as_module_paths)
