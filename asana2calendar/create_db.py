"""Creates sqlite3 tables to save the sync state to use later."""
import os
from sqlite3 import connect


def create_tables():
    if os.environ["XDG_DATA_DiR"]:
        path = os.environ["XDG_DATA_DIR"] + "/asana2calendar/sync.db"
    else:
        path = os.environ["HOME"] + "/.local/share/asana2calendar/sync.db"

    # Create a connection to the database
    conn = connect(path)

    # Create a cursor object
    cursor = conn.cursor()

    # Create the asana table
    cursor.execute(
        """
    CREATE TABLE asana (
        id INTEGER PRIMARY KEY,
        date DATE,
        task VARCHAR(255),
        location VARCHAR(255),
        due_date DATETIME,
        start_date DATETIME,
        modified_date DATETIME,
        completed BOOLEAN
    )
    """
    )

    # Create the calendar table
    cursor.execute(
        """
    CREATE TABLE calendar (
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

    # Create the linked table
    cursor.execute(
        """
    CREATE TABLE task_event_connection (
        id INTEGER PRIMARY KEY,
        asana_id INTEGER,
        calendar_id INTEGER,
        FOREIGN KEY(asana_id) REFERENCES asana(id),
        FOREIGN KEY(calendar_id) REFERENCES calendar(id)
    )
    """
    )

    # Commit the changes to the database
    conn.commit()

    # Close the connection
    conn.close()


if __name__ == "__main__":
    create_tables()
