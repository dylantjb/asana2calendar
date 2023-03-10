"""Fetch tasks from project and creates an event in respective caldav calendar."""
import argparse
import os
from pathlib import Path

from .__about__ import __version__ as version
from .core.config import (
    create_config,
    get_enabled_plugins,
    parse_config,
    validate_plugins,
)
from .core.database import create_tables, fetch_database
from .core.sync import CalendarSync


def main():
    """
    Entry point for the asana2calendar application. Parses arguments,
    creates a configuration file or database, loads the configuration file,
    creates an instance of the CalendarSync class, and starts the sync process.
    Usage:
        To create a new configuration file, use the following command:
        `python -m asana2calendar --create-config [<path>]`

        To create a new database file, use the following command:
        `python -m asana2calendar --create-db [<path>]`

        To sync the calendar, use the following command:
        `python -m asana2calendar [--config-file <path>] [--db-file <path>]`
    """

    # Tries the XDG Base Directory Specification for unix systems
    xdg_config_dir = Path(os.environ.get("XDG_CONFIG_DIR", "~/.config")).expanduser()
    xdg_data_dir = Path(os.environ.get("XDG_DATA_DIR", "~/.local/share")).expanduser()
    config_file = (
        xdg_config_dir / "asana2calendar" / "config.ini"
        if (xdg_config_dir.exists())
        else Path.home() / ".asana2calendar" / "config.ini"
    )
    db_file = (
        xdg_data_dir / "asana2calendar" / "sync.db"
        if (xdg_data_dir.exists())
        else Path.home() / ".asana2calendar" / "sync.db"
    )

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
    parser.add_argument(
        "-c",
        "--config-file",
        metavar="CONFIG_PATH",
        default=config_file,
        help="Custom path for the configuration file. "
        "If not provided, the default path will be used.",
    )
    parser.add_argument(
        "-d",
        "--db-file",
        metavar="DB_PATH",
        default=db_file,
        help="Custom path for the database file.\n"
        "If not provided, the default path will be used.",
    )
    parser.add_argument(
        "--create-config",
        metavar="CONFIG_PATH",
        nargs="?",
        const=config_file,
        help="Create a new configuration file. "
        "If not provided, the default path will be used.",
    )
    parser.add_argument(
        "--create-db",
        metavar="DB_PATH",
        nargs="?",
        const=db_file,
        help="Create a new database file. "
        "Your configuration file will be used. Supply it with --config-file <path>.\n"
        "If not provided, default paths will be used.",
    )
    args = parser.parse_args()

    if args.create_config:
        print(f"Generating configuration file at {args.create_config}...")
        args.create_config.parent.mkdir(exist_ok=True)
        create_config(args.create_config)
        return

    if args.config_file.exists():
        enabled_plugins = get_enabled_plugins(args.config_file)
    else:
        print(f"No configuration file not found at {args.config_file}")
        return

    if args.create_db:
        if validate_plugins(enabled_plugins):
            print(f"Generating database file at {args.create_db}...")
            if args.db_file.exists():
                args.db_file.unlink()
            create_tables(args.create_db, enabled_plugins)
        else:
            print("Invalid configuration. Fix or create one with --create-config.")
        return

    if args.config_file.exists() and args.config_file.exists():
        plugins = parse_config(enabled_plugins)
        try:
            conn = fetch_database(args.db_file, list(enabled_plugins.keys()))
        except ValueError as exc:
            print(exc)
            print("See --help to see how to create this.")
            return
    else:
        print(
            "Configuration or database files do not exist at default or supplied locations."
        )
        return

    CalendarSync(plugins, conn).sync()


if __name__ == "__main__":
    main()
