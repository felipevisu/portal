from unittest import mock

import pytest
from django.http import HttpResponseNotFound

from ..manager import PluginsManager, get_plugins_manager
from .sample_plugins import (
    ACTIVE_PLUGINS,
    ALL_PLUGINS,
    ChannelPluginSample,
    PluginSample,
)

pytestmark = pytest.mark.django_db


def test_get_plugins_manager(settings):
    plugin_path = "portal.plugins.tests.sample_plugins.PluginSample"
    settings.PLUGINS = [plugin_path]
    manager = get_plugins_manager()
    assert isinstance(manager, PluginsManager)
    assert len(manager.all_plugins) == 1


def test_manager_with_default_configuration_for_channel_plugins(
    settings, channel_city_1, channel_city_2
):
    settings.PLUGINS = [
        "portal.plugins.tests.sample_plugins.ChannelPluginSample",
        "portal.plugins.tests.sample_plugins.PluginSample",
    ]
    manager = get_plugins_manager()
    assert len(manager.global_plugins) == 1
    assert isinstance(manager.global_plugins[0], PluginSample)
    assert {channel_city_1.slug, channel_city_2.slug} == set(
        manager.plugins_per_channel.keys()
    )

    for channel_slug, plugins in manager.plugins_per_channel.items():
        assert len(plugins) == 2
        assert all(
            [
                isinstance(plugin, (PluginSample, ChannelPluginSample))
                for plugin in plugins
            ]
        )

    # global plugin + plugins for each channel
    assert len(manager.all_plugins) == 3


def test_manager_with_channel_plugins(
    settings, channel_city_1, channel_city_2, channel_plugin_configurations
):
    settings.PLUGINS = [
        "portal.plugins.tests.sample_plugins.ChannelPluginSample",
    ]
    manager = get_plugins_manager()

    assert {channel_city_1.slug, channel_city_2.slug} == set(
        manager.plugins_per_channel.keys()
    )

    for channel_slug, plugins in manager.plugins_per_channel.items():
        assert len(plugins) == 1
        # make sure that we load proper config from DB
        assert plugins[0].configuration[0]["value"] == channel_slug

    # global plugin + plugins for each channel
    assert len(manager.all_plugins) == 2


def test_manager_get_plugins_with_channel_slug(
    settings, channel_city_1, plugin_configuration, inactive_plugin_configuration
):
    settings.PLUGINS = [
        "portal.plugins.tests.sample_plugins.PluginInactive",
        "portal.plugins.tests.sample_plugins.PluginSample",
    ]
    manager = get_plugins_manager()

    plugins = manager.get_plugins(channel_slug=channel_city_1.slug)

    assert plugins == manager.plugins_per_channel[channel_city_1.slug]


def test_manager_get_active_plugins_with_channel_slug(
    settings, channel_city_1, plugin_configuration, inactive_plugin_configuration
):
    settings.PLUGINS = [
        "portal.plugins.tests.sample_plugins.PluginInactive",
        "portal.plugins.tests.sample_plugins.PluginSample",
    ]
    manager = get_plugins_manager()

    plugins = manager.get_plugins(channel_slug=channel_city_1.slug, active_only=True)

    assert len(plugins) == 1
    assert isinstance(plugins[0], PluginSample)


def test_manager_get_plugins_without_channel_slug(
    settings, channel_city_1, plugin_configuration, inactive_plugin_configuration
):
    settings.PLUGINS = [
        "portal.plugins.tests.sample_plugins.PluginInactive",
        "portal.plugins.tests.sample_plugins.PluginSample",
    ]
    manager = get_plugins_manager()

    plugins = manager.get_plugins(channel_slug=None)

    assert plugins == manager.all_plugins


def test_manager_get_active_plugins_without_channel_slug(
    settings, channel_city_1, plugin_configuration, inactive_plugin_configuration
):
    settings.PLUGINS = [
        "portal.plugins.tests.sample_plugins.PluginInactive",
        "portal.plugins.tests.sample_plugins.PluginSample",
    ]
    manager = get_plugins_manager()

    plugins = manager.get_plugins(channel_slug=None, active_only=True)

    assert len(plugins) == 1
    assert isinstance(plugins[0], PluginSample)


def test_run_method_on_plugins_default_value(plugins_manager):
    default_value = "default"
    value = plugins_manager._PluginsManager__run_method_on_plugins(
        method_name="test_method",
        default_value=default_value,
    )

    assert value == default_value


def test_run_method_on_plugins_default_value_when_not_existing_method_is_called(
    channel_city_1, all_plugins_manager
):
    default_value = "default"
    value = all_plugins_manager._PluginsManager__run_method_on_plugins(
        method_name="test_method",
        default_value=default_value,
    )

    assert value == default_value


@mock.patch(
    "portal.plugins.manager.PluginsManager._PluginsManager__run_method_on_single_plugin"
)
def test_run_method_on_plugins_only_on_active_ones(
    mocked_method, channel_city_1, all_plugins_manager
):
    all_plugins_manager._PluginsManager__run_method_on_plugins(
        method_name="test_method_name",
        default_value="default_value",
    )
    active_plugins_count = len(ACTIVE_PLUGINS)

    assert len(all_plugins_manager.all_plugins) == len(ALL_PLUGINS)
    assert (
        len([p for p in all_plugins_manager.all_plugins if p.active])
        == active_plugins_count
    )
    assert mocked_method.call_count == active_plugins_count

    called_plugins_id = [arg.args[0].PLUGIN_ID for arg in mocked_method.call_args_list]
    expected_active_plugins_id = [p.PLUGIN_ID for p in ACTIVE_PLUGINS]

    assert called_plugins_id == expected_active_plugins_id
