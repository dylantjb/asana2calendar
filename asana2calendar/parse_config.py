"""
config_parser.py - a script for parsing a configuation file.

Usage: python config_parser [config_file_path]

Requirements: Python 3.x

Author: Dylan Barker
Date: 07/04/2023
"""
import configparser
import importlib
from os.path import exists


def load_plugins_from_config(config_file_path):
    """
    Loads plugins from a configuration file and returns a list of plugin instances.

    Args:
        config_file_path (str): The path to the configuration file.

    Returns:
        A list of plugin instances.

    Raises:
        FileNotFoundError: If the configuration file cannot be found in the provided path.
        NoSectionError: If the plugins section is not found.
        ValueError: If less than two plugins are enabled and/or without the required fields.
                    The required plugin must also be enabled.
        KeyError: Section in configuration file is not recognised as a valid plugin.
    """

    plugins = {}

    # Define the required plugins and fields
    required_plugin = "asana"
    required_fields = {
        "asana": ["pat", "name"],
        "caldav": ["url", "username", "password"],
    }

    config = configparser.ConfigParser()
    if not exists(config_file_path):
        raise FileNotFoundError("No config file detected in correct path.")
    config.read(config_file_path)

    # Load enabled plugins from 'plugins' section
    try:
        enabled_plugins = [
            k for k, v in dict(config.items("plugins")).items() if v == "true"
        ]
    except configparser.NoSectionError:
        print("No plugins section.")
        exit()

    # Check if required plugin is present and at least two plugins enabled
    if len(enabled_plugins) < 2 or required_plugin not in enabled_plugins:
        raise ValueError(
            f'At least two plugins must be enabled and plugin "{required_plugin}" is required.'
        )

    for plugin_name in enabled_plugins:
        try:
            for fields in required_fields[plugin_name]:
                if all(field in fields for field in config[plugin_name]):
                    raise ValueError(
                        f'{plugin_name} must have fields: {", ".join(fields)}'
                    )
        except KeyError:
            print(f'Unknown plugin "{plugin_name}".')
            continue

        plugin_module = importlib.import_module("plugins." + plugin_name)
        plugin_class_name = plugin_name.title() + "Calendar"
        plugins[getattr(plugin_module, plugin_class_name)] = dict(config[plugin_name])

    # Return the list of plugin instances
    return plugins


# TODO: Validate fields to regex (e.g. urls, pat)
