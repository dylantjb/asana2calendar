"""
config.py - a script for parsing a configuation file.

Requirements: Python 3.x
"""
import configparser
import importlib
import sys
from os.path import exists


def get_enabled_plugins(config_file_path):
    """
    Returns a list of enabled plugins, as specified in the 'plugins'
    section of the provided config file.

    Args:
        config_file_path (str): The path to the configuration file.

    Returns:
        A tuple containing a list of enabled plugins and the parsed configparser object.

    Raises:
        FileNotFoundError: If the specified config file does not exist.
        configparser.NoSectionError: If the 'plugins' section is missing from the config file.
    """
    config = configparser.ConfigParser()
    if not exists(config_file_path):
        raise FileNotFoundError("No config file detected in correct path.")
    config.read(config_file_path)

    # Load enabled plugins from 'plugins' section
    try:
        return [
            k for k, v in dict(config.items("plugins")).items() if v == "true"
        ], config
    except configparser.NoSectionError:
        sys.exit("No plugin section.")


def load_config(config_file_path):
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
    required_fields = {
        "asana": ["pat", "name"],
        "caldav": ["url", "username", "password"],
    }

    enabled_plugins, config = get_enabled_plugins(config_file_path)

    # Check if required plugin is present and at least two plugins enabled
    if len(enabled_plugins) < 2 or "asana" not in enabled_plugins:
        raise ValueError(
            "At least two plugins must be enabled and the plugin asana is required."
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


def create_config(path):
    """
    Creates a new configuration file based on user input.

    The function prompts the user to enter configuration values for each section
    of the configuration file, and then writes the resulting configuration file
    to disk. The user must create the 'asana_plugin' section and at least one other
    section in order for the function to create a configuration file.

    Returns:
        None
    """
    config = configparser.ConfigParser()

    # Set the default values for each section
    config["asana"] = {"api": "", "name": ""}
    config["caldav"] = {
        "username": "",
        "password": "",
        "url": "",
    }

    # Prompt the user to enter values for each section
    for section in config.sections():
        if section == "plugins":
            continue
        choice = input(f'Create configuration for "{section}"? [Y/n]:')
        if not choice.lower() == "n":
            for key in config[section]:
                value = input(f"{key}: ")
                if value:
                    config[section][key] = value
            config["plugins"][section] = "true"

    # Make sure the user has created at least two sections and the asana plugin section
    if len(config["plugins"]) < 2 or not config["plugins"].get("asana"):
        print(
            "You must create at least two configuration sections, including the 'asana' section."
        )
        return

    # Write the config file to disk
    with open(path, "w", encoding="UTF") as configfile:
        config.write(configfile)


# TODO: Validate fields to regex (e.g. urls, pat)
