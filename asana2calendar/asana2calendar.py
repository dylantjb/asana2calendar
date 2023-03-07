"""Fetch tasks from project and creates an event in respective caldav calendar."""
import os
import sqlite3

from .create_config import create_config_file
from .create_db import create_tables
from .parse_config import load_plugins_from_config
from .sync import CalendarSync


def main():
    if os.environ["XDG_CONFIG_DIR"] and os.environ["XDG_DATA_DiR"]:
        config_file = os.environ["XDG_CONFIG_DIR"] + "/asana2calendar/config.ini"
        db_file = os.environ["XDG_DATA_DIR"] + "/asana2calendar/sync.db"
    else:
        config_file = os.environ["HOME"] + "/.config/asana2calendar/config.ini"
        db_file = os.environ["HOME"] + "/.local/share/asana2calendar/sync.db"

    try:
        load_plugins_from_config(config_file)
        sqlite3.connect(db_file)
    except FileNotFoundError as exc:
        print(exc)
        if input("Would you like to create your configuration? [Y/n] ").lower() != "n":
            create_config_file()
        else:
            return
    except sqlite3.DatabaseError:
        print("No database detected in correct path.")
        if input("Would you like to create your database? [Y/n] ").lower() != "n":
            create_tables()
        else:
            return

    conn = sqlite3.connect("sync.db")
    CalendarSync(load_plugins_from_config(config_file), conn).sync()


if __name__ == "__main__":
    main()
