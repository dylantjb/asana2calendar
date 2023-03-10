import os
import sqlite3

import pytest

from asana2calendar.core.database import create_tables, fetch_database


@pytest.fixture(scope="module")
def test_db_path():
    """Fixture to set up the test database."""
    db_path = "test_db.sqlite"
    yield db_path
    # Teardown: Remove the test database file
    os.remove(db_path)


def test_create_tables(test_db_path):
    """Test the create_tables method."""
    # Define test data
    enabled_plugins = ["plugin1", "plugin2"]

    # Call the method
    create_tables(test_db_path, enabled_plugins)

    # Assert that the tables have been created
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    for plugin_name in enabled_plugins:
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{plugin_name}';"
        )
        result = cursor.fetchone()
        assert result is not None, f"Table '{plugin_name}' not found."
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='event_connection';"
    )
    result = cursor.fetchone()
    assert result is not None, "Table 'event_connection' not found."

    # Teardown: Remove the tables from the test database
    for plugin_name in enabled_plugins:
        cursor.execute(f"DROP TABLE {plugin_name};")
    cursor.execute("DROP TABLE event_connection;")
    conn.commit()
    conn.close()


def test_fetch_database(test_db_path):
    """Test the fetch_database method."""
    # Define test data
    enabled_plugins = ["plugin1", "plugin2"]

    # Call the method after creating tables
    create_tables(test_db_path, enabled_plugins)
    conn = fetch_database(test_db_path, enabled_plugins)

    # Assert that the method returns the database connection
    assert isinstance(conn, sqlite3.Connection)

    # Teardown: Remove the tables from the test database
    cursor = conn.cursor()
    for plugin_name in enabled_plugins:
        cursor.execute(f"DROP TABLE {plugin_name};")
    cursor.execute("DROP TABLE event_connection;")
    conn.commit()
    conn.close()


def test_fetch_database_with_wrong_tables(test_db_path):
    """Test the fetch_database method when the tables are not configured correctly."""
    # Define test data
    enabled_plugins = ["plugin1", "plugin2"]

    # Call the method before creating tables
    with pytest.raises(
        ValueError, match="Tables in database not configured correctly."
    ):
        conn = fetch_database(test_db_path, enabled_plugins)

    # Teardown: None needed, since the tables have not been created
