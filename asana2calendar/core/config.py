"""
config.py - a script for parsing a configuation file.

Requirements: Python 3.x
"""
import configparser
import importlib
import re


def load_config(config_file_path):
    config = configparser.ConfigParser()
    assert config_file_path.exists()
    config.read(config_file_path)
    return config


def get_enabled_plugins(config_file_path):
    """
    Returns a list of enabled plugins, as specified in the 'plugins'
    section of the provided config file.

    Args:
        config_file_path (str): The path to the configuration file.

    Returns:
        A tuple containing a list of enabled plugins and the parsed configparser object.
    """
    config = load_config(config_file_path)

    # Load enabled plugins from 'plugins' section
    try:
        enabled = [k for k, v in dict(config.items("plugins")).items() if v == "True"]
    except configparser.NoSectionError as exc:
        raise SystemExit("No plugin section in configuration file.") from exc

    return {enb: dict(config.items(enb)) for enb in enabled}


def validate_plugins(plugins):
    regex_fields = {
        "asana": {"pat": r"^1/(\d{16}):([0-9a-f]{32})$"},
        "caldav": {"url": r"^(webcal[s]?|http[s]?):\/\/(?:[\w-]+\.)+[a-z]{2,}"},
    }
    required_fields = {
        "asana": ["pat", "name"],
        "caldav": ["url", "username", "password"],
    }

    if len(plugins) < 2 or "asana" not in plugins.keys():
        raise SystemExit(
            "At least two plugins must be enabled and the asana plugin is required."
        )

    for plugin_name, data in plugins.items():  # validate all the fields
        try:
            fields = required_fields[plugin_name]
        except KeyError:
            print(f'Plugin "{plugin_name}" is unknown.')
            continue

        for field in fields:
            try:
                config_field = data[field]
            except KeyError:
                print(f'Field "{field}" is required for "{plugin_name}" plugin.')
                return False

            try:
                regex_field = re.compile(regex_fields[plugin_name][field])
                if not regex_field.match(config_field):
                    print(f"{plugin_name}: {field} does not conform to standard.")
                    return False
            except KeyError:  # No regex necesary for this field
                pass
    return True


def parse_config(enabled_plugins):
    """
    Loads plugins from a configuration file and returns a list of plugin instances.

    Args:
        config_file_path (str): The path to the configuration file.

    Returns:
        A list of plugin instances.

    Throws:
        FileNotFoundError: If the configuration file cannot be found in the provided path.
    """

    # {{ClassName: data}, }
    plugins = {}

    if validate_plugins(enabled_plugins):
        for plugin_name in enabled_plugins:
            plugin_module = importlib.import_module(
                "asana2calendar.plugins." + plugin_name
            )
            plugin_class_name = plugin_name.title() + "Calendar"
            plugins[getattr(plugin_module, plugin_class_name)] = dict(
                enabled_plugins[plugin_name]
            )

    return plugins


def create_config(path):
    """
    Creates a new configuration file based on user input.

    The function prompts the user to enter configuration values for each section
    of the configuration file, and then writes the resulting configuration file
    to disk. The user must create the 'asana' section and at least one other
    section in order for the function to create a configuration file.

    Returns:
        None
    """
    config = configparser.ConfigParser()

    # Set the default values for each section
    config["plugins"] = {}
    config["asana"] = {"pat": "", "name": ""}
    config["caldav"] = {
        "username": "",
        "password": "",
        "url": "",
    }

    # Prompt the user to enter values for each section
    for section in config.sections():
        if section == "plugins":
            continue
        choice = input(f'Create configuration for "{section}"? [Y/n]: ')
        if not choice.lower() == "n":
            for key in config[section]:
                value = input(f"{key}: ")
                if value:
                    config[section][key] = value
            config["plugins"][section] = "True"

    # Make sure the user has created at least two sections and the asana plugin section
    if len(config["plugins"]) < 2 or not config["plugins"].get("asana"):
        print(
            "You must create at least two configuration sections, including the 'asana' section."
        )
        return

    # Write the config file to disk
    with open(path, "w", encoding="UTF") as configfile:
        config.write(configfile)
