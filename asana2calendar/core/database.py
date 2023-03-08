"""
database.py - a script for creating tables in a sqlite3 database to store the sync state.

Requirements: Python 3.x
"""
from sqlite3 import connect

from asana2calendar.core.config import get_enabled_plugins


def create_tables(db_path, config_file_path):
    """
    Creates tables in the SQLite database specified by `db_path`.
    The tables are created based on the enabled plugins specified in the configuration file
    located at `config_file_path`.

    Args:
        db_path (str): The path to the SQLite database.
        config_file_path (str): The path to the configuration file.

    Returns:
        None
    """
    enabled_plugins, _ = get_enabled_plugins(config_file_path)
    conn = connect(db_path)
    cursor = conn.cursor()

    id_query = ""
    foreign_query = ""
    for plugin, _ in enabled_plugins:
        id_query += f"{plugin}_id INTEGER, "
        foreign_query += f"FOREGIN KEY(f{plugin}_id) REFERENCES {plugin}(id), "
        cursor.execute(
            f"""
            CREATE TABLE {plugin} (
                id INTEGER PRIMARY KEY,
                date DATE,
                event VARCHAR(255),
                location VARCHAR(255),
                due_date DATETIME,
                start_date DATETIME,
                modified_date DATETIME,
                completed BOOLEAN
            )
            """
        )

    cursor.execute(
        "CREATE TABLE event_connection ( id INTEGER PRIMARY KEY, "
        + id_query
        + foreign_query
        + " )"
    )

    # Commit the changes to the database
    conn.commit()

    # Close the connection
    conn.close()
