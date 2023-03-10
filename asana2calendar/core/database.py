"""
database.py - a script for creating tables in a sqlite3 database to store the sync state.

Requirements: Python 3.x
"""
from sqlite3 import connect


def create_tables(db_path, enabled_plugins):
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
    conn = connect(db_path)
    cursor = conn.cursor()

    id_statement = []
    foreign_statement = []
    for plugin_name in enabled_plugins:
        id_statement.append(f", {plugin_name}_id INTEGER")
        foreign_statement.append(
            f", FOREIGN KEY({plugin_name}_id) REFERENCES {plugin_name}(id)"
        )
        cursor.execute(
            f"""
            CREATE TABLE {plugin_name} (
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
        "CREATE TABLE event_connection ( id INTEGER PRIMARY KEY"
        + "".join(id_statement)
        + "".join(foreign_statement)
        + " )"
    )

    # Commit the changes to the database
    conn.commit()

    # Close the connection
    conn.close()


def fetch_database(db_path, enabled_plugins):
    conn = connect(db_path)
    cursor = conn.cursor()
    for plugin_name in enabled_plugins:
        cursor.execute(f"PRAGMA table_info('{plugin_name}');")
        if cursor.fetchone() is None:
            raise ValueError("Tables in database not configured correctly.")
    return conn
