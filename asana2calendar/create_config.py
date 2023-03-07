"""
config_creator.py - a script for creating a configuration file.

Usage: python config_creator.py

Requirements: Python 3.x

Author: Dylan Barker
Date: 07/04/2023
"""
import configparser


def create_config_file():
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
    required_plugin = "asana"
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
    if len(config["plugins"]) < 2 or not config["plugins"].get(required_plugin):
        print(
            "You must create at least two configuration sections, including the 'asana' section."
        )
        return

    # Write the config file to disk
    with open("config.ini", "w", encoding="UTF") as configfile:
        config.write(configfile)


if __name__ == "__main__":
    create_config_file()
