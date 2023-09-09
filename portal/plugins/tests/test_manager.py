from unittest import mock

import pytest

from ..manager import PluginsManager, get_plugins_manager
from .sample_plugins import ACTIVE_PLUGINS, ALL_PLUGINS, PluginSample

pytestmark = pytest.mark.django_db


def test_get_plugins_manager(settings):
    plugin_path = "portal.plugins.tests.sample_plugins.PluginSample"
    settings.PLUGINS = [plugin_path]
    manager = get_plugins_manager()
    assert isinstance(manager, PluginsManager)
    assert len(manager.all_plugins) == 1


def test_run_method_on_plugins_default_value(plugins_manager):
    default_value = "default"
    value = plugins_manager._PluginsManager__run_method_on_plugins(
        method_name="test_method",
        default_value=default_value,
    )

    assert value == default_value


def test_run_method_on_plugins_default_value_when_not_existing_method_is_called(
    all_plugins_manager,
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
def test_run_method_on_plugins_only_on_active_ones(mocked_method, all_plugins_manager):
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
