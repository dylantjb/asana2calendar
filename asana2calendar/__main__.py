"""Fetch tasks from project and creates an event in respective caldav calendar."""
import argparse
import json
import re
from getpass import getpass
from importlib import import_module
from pathlib import Path

import keyring
from platformdirs import PlatformDirs

from .__about__ import __version__ as version
from .core.database import create_tables, fetch_database
from .core.sync import CalendarSync


def config_caldav():
    config_dict = {}
    print("Configuring plugin: caldav")
    config_dict["username"] = input("Username: ")
    config_dict["password"] = getpass("Password: ")
    while True:
        config_dict["url"] = input("URL: ")
        if not re.compile(r"^(webcal[s]?|http[s]?):\/\/(?:[\w-]+\.)+[a-z]{2,}").match(
            config_dict["url"]
        ):
            print("URL does not match webdav specification.")
        else:
            break

    keyring.set_password("asana2calendar", "caldav", json.dumps(config_dict))


def delete_plugins(plugins):
    for plugin_name in plugins:
        keyring.delete_password("asana2calendar", plugin_name)


def get_plugins():
    plugin_dir = Path(__file__).resolve().parent / "plugins"
    return [
        f.stem
        for f in plugin_dir.glob("*.py")
        if f.name not in ("__init__.py", "base.py", "asana.py")
    ]


def get_enabled_plugins():
    return [
        plugin_name
        for plugin_name in get_plugins()
        if keyring.get_password("asana2calendar", plugin_name)
    ]


def get_calendar_class(plugin_name):
    plugin_module = import_module("asana2calendar.plugins." + plugin_name)
    plugin_class_name = plugin_name.title() + "Calendar"
    return getattr(plugin_module, plugin_class_name)


def main():
    """
    Entry point for the asana2calendar application. Parses arguments,
    creates a configuration file or database, loads the configuration file,
    creates an instance of the CalendarSync class, and starts the sync process.
    Usage:
    """
    # Create argparse parser
    parser = argparse.ArgumentParser(description="Sync Asana tasks with a calendar.")

    # Add arguments to the parser
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=version,
        help="Show asana2calendar's version number and exit",
    )
    parser = argparse.ArgumentParser(description="Plugin Configuration")
    parser.add_argument(
        "-p",
        "--plugins",
        metavar="PLUGIN_NAME",
        nargs="*",
        help="Choose plugin(s).",
    )
    parser.add_argument(
        "-d",
        "--delete",
        metavar="PLUGIN_NAME",
        nargs="*",
        help="Delete the plugin(s) details.",
    )
    parser.add_argument(
        "-s",
        "--show",
        action="store_true",
        help="Show the plugin(s) details.",
    )
    args = parser.parse_args()

    if args.delete:
        delete_plugins(args.delete)
        print("Plugins deleted.")
        return

    if args.show:
        for plugin_name in get_plugins():
            print(f"Settings for {plugin_name}...")
            data = keyring.get_password("asana2calendar", plugin_name)
            assert data
            if plugin_name == "caldav":
                for k, value in json.loads(data).items():
                    print(f"{k}: {value}")
                print()
                continue
            get_calendar_class(plugin_name)(**json.loads(data)).showinfo()
            print()
        return

    if args.init:
        for plugin_name in args.init:
            if plugin_name == "caldav":  # No OAuth for generic caldav calendar
                config_caldav()
                continue
            keyring.set_password(
                "asana2calendar",
                plugin_name,
                json.dumps(get_calendar_class(plugin_name)().TOKEN),
            )

        db_path = (
            Path(PlatformDirs("asana2calendar", "dylantjb").user_data_dir) / "sync.db"
        )
        db_path.parent.mkdir(parents=True, exist_ok=True)
        if db_path.exists():
            db_path.unlink()
        create_tables(db_path, args.init)
        return

        # enabled_plugins = get_plugins()
        # db_path = (
        #     Path(PlatformDirs("asana2calendar", "dylantjb").user_data_dir) / "sync.db"
        # )
        # if not (db_path and enabled_plugins):
        #     print("Run --set to setup your desired plugins.")
        # conn = fetch_database(db_path, enabled_plugins)

        # plugins = {}
        # for plugin_name in enabled_plugins:
        #     data = keyring.get_password("asana2calendar", plugin_name)
        #     assert data
        #     plugins[get_calendar_class(plugin_name)] = json.loads(data)

        # CalendarSync(conn, **plugins)

    # CalendarSync(plugins, conn).sync()


if __name__ == "__main__":
    main()
