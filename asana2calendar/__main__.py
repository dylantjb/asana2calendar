"""Fetch tasks from project and creates an event in respective caldav calendar."""
import argparse
import os
import sqlite3

from asana2calendar.core.config import create_config, load_config
from asana2calendar.core.database import create_tables
from asana2calendar.core.sync import CalendarSync


def main():
    """
    Entry point for the asana2calendar application. Parses arguments, 
    creates a configuration file or database, loads the configuration file,
    creates an instance of the CalendarSync class, and starts the sync process.
    """

    # Tries the XDG Base Directory Specification for unix systems
    if os.environ.get("XDG_CONFIG_DIR") and os.environ.get("XDG_DATA_DIR"):
        config_file = os.environ["XDG_CONFIG_DIR"] + "/asana2calendar/config.ini"
        db_file = os.environ["XDG_DATA_DIR"] + "/asana2calendar/sync.db"
    else:
        config_file = os.environ["HOME"] + "/.config/asana2calendar/config.ini"
        db_file = os.environ["HOME"] + "/.local/share/asana2calendar/sync.db"

    parser = argparse.ArgumentParser(
        description="Create a database or configuration file."
    )
    parser.add_argument(
        "action",
        choices=["create-config", "create-database"],
        help="Generate your configuration or database",
    )
    parser.add_argument(
        "--config-path",
        default=config_file,
        help="Custom path for the configuration file.",
    )
    parser.add_argument(
        "--db-path", default=db_file, help="Custom path for the database file"
    )

    args = parser.parse_args()
    if args.action == "create-config":
        print(f"Creating configuration file at {args.db_path}...")
        create_config(args.config_path)
    if args.action == "create-database":
        load_config(
            args.config_path
        )  # Performs validation to ensure it's suitable for database
        print(f"Creating database at {args.config_path}...")
        create_tables(args.db_path, args.config_path)

    try:
        plugins = load_config(args.config_path)
        conn = sqlite3.connect(args.db_path)
    except FileNotFoundError as exc:
        print(exc)
        print(
            "Create a configuration file using config.example.ini or run program with options:"
        )
        print("Refer to --help to know how to do this.")
        return

    CalendarSync(plugins, conn).sync()


if __name__ == "__main__":
    main()

# TODO: Consider using argparse for user access to creating database and config file
