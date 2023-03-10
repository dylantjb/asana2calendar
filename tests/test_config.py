import configparser
from unittest.mock import MagicMock, patch

import pytest

from asana2calendar.core.config import (
    create_config,
    get_enabled_plugins,
    load_config,
    parse_config,
    validate_plugins,
)


@pytest.fixture(scope="module")
def config_file(tmpdir_factory):
    config = """
    [plugins]
    asana=True
    caldav=True
    
    [asana]
    pat=1/1204012332645812:4e70460205da46c60fd6efa9d5166346
    name=Test
    
    [caldav]
    url=http://example.com
    username=test
    password=test
    """
    config_file = tmpdir_factory.mktemp("data").join("config.ini")
    with open(str(config_file), "w", encoding="UTF") as file:
        file.write(config)
    return config_file


def test_load_config(config_file):
    config = load_config(config_file)
    assert isinstance(config, configparser.ConfigParser)
    assert (
        config.get("asana", "pat")
        == "1/1204012332645812:4e70460205da46c60fd6efa9d5166346"
    )


def test_get_enabled_plugins(config_file):
    plugins = get_enabled_plugins(config_file)
    assert isinstance(plugins, dict)
    assert len(plugins) >= 2
    assert "asana" in plugins
    assert "caldav" in plugins


def test_validate_plugins():
    plugins = {
        "asana": {
            "pat": "1/1204012332645812:4e70460205da46c60fd6efa9d5166346",
            "name": "Test",
        },
        "caldav": {"url": "http://example.com", "username": "test", "password": "test"},
    }
    assert validate_plugins(plugins) is True


class MockAsanaCalendar:
    pass


class MockCaldavCalendar:
    pass


@patch("asana2calendar.core.config.importlib")
def test_parse_config(mock_importlib):
    enabled_plugins = {
        "asana": {
            "pat": "1/1234567890123456:1234567890abcdef1234567890abcdef",
            "name": "Test",
        },
        "caldav": {
            "url": "https://example.com/calendar",
            "username": "user",
            "password": "pass",
        },
    }

    mock_module = MagicMock()
    mock_module.AsanaCalendar = MockAsanaCalendar
    mock_module.CaldavCalendar = MockCaldavCalendar
    mock_importlib.import_module.return_value = mock_module

    plugins = parse_config(enabled_plugins)
    assert len(plugins) == 2
    assert list(plugins.keys())[0] == MockAsanaCalendar
    assert list(plugins.keys())[1] == MockCaldavCalendar


def test_create_config(tmpdir):
    config_path = tmpdir.join("config.ini")
    user_input = iter(
        [
            "y",
            "1/1204012332645812:4e70460205da46c60fd6efa9d5166346",
            "testName",
            "y",
            "testUsername",
            "testPassword",
            "http://example.com",
        ]
    )

    with patch("builtins.input", lambda _: next(user_input)):
        create_config(config_path)

    assert config_path.exists()
    config = load_config(config_path)

    assert (
        config.get("asana", "pat")
        == "1/1204012332645812:4e70460205da46c60fd6efa9d5166346"
    )
    assert config.get("asana", "name") == "testName"
    assert config.get("caldav", "username") == "testUsername"
    assert config.get("caldav", "password") == "testPassword"
    assert config.get("caldav", "url") == "http://example.com"
