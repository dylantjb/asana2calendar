"""
sync.py - A tool for synchronizing events between multiple calendars.

This file provides a command line interface for synchronizing events between multiple
calendars, including the Asana and Caldav Calendars.

The tool provides the following functionality:
- Two-way syncing of events between multiple calendars
- Support for multiple calendars and events per calendar
- Customizable database creation
- Plugin architecture for extending functionality
"""


class CalendarSync:  # pylint: disable=too-few-public-methods
    """
    A class for syncing events between two calendars.

    Args:
        calendars (list): A list of tuples containing the names of the calendars and
                          the names of the tables in the database where the events are stored.
        conn (sqlite3.Connection): A SQLite database connection object.

    Attributes:
        conn (sqlite3.Connection): A SQLite database connection object.
        calendars (list): A list of calendar objects representing the calendars being synced.

    Methods:
        sync(): Syncs events between the two calendars.
        _sync_event(calendar_event, calendar_event): Syncs a single event between the two calendars.
        _get_calendar_events(): Retrieves all events from the calendar.
        _update_calendar_event(event_id, name, modified_date):
            Updates an event in the calendar.
        _update_calendar_event(event_id, name, modified_date):
            Updates a event in the calendar calendar.
    """

    def __init__(self, conn, **calendars):
        """
        Initializes a new instance of the CalendarSync class.

        Args:
            calendars (list): A list of tuples containing the names of the calendars
            and the names of the tables in the database where the events are stored.
            conn (sqlite3.Connection): A SQLite database connection object.
        """
        self.conn = conn
        print(calendars.items())
        # self.calendars = [c(d) for c, d in calendars.items()]

    def sync(self):
        """Syncs events between the two calendars."""

    #     # Retrieve all events from both calendars
    #     calendar_events = self._get_calendar_events()
    #     calendar_events = self._get_calendar_events()

    #     # Sync each event in both directions
    #     for calendar_event in calendar_events:
    #         for calendar_event in calendar_events:
    #             if calendar_event["id"] == calendar_event["id"]:
    #                 self._sync_event(calendar_event, calendar_event)

    # def _sync_event(self, calendar_event, calendar_event):
    #     # Check which event has a more recent modified_date
    #     if calendar_event["modified_date"] > calendar_event["modified_date"]:
    #      # calendar event has a more recent modified_date, update the corresponding calendar event
    #         self._update_calendar_event(
    #             calendar_event["id"], calendar_event["name"], calendar_event["modified_date"]
    #         )
    #     elif calendar_event["modified_date"] > calendar_event["modified_date"]:
    #       # Calendar event has a more recent modified_date, update the corresponding calendar task
    #         self._update_calendar_task(
    #             calendar_event["id"],
    #             calendar_event["name"],
    #             calendar_event["modified_date"],
    #         )

    def _get_calendar_events(self):
        """
        Retrieves all events from the calendar.

        Returns:
            A list of dictionaries representing events in the calendar.
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM calendar")
        return cursor.fetchall()

    def _update_calendar_event(self, event_id, name, modified_date):
        """
        Updates all specific task in the calendar.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            f"""
            UPDATE calendar
            SET name={name}, modified_date={modified_date}
            WHERE id={event_id}
            """
        )
        self.conn.commit()

    def _delete_calendar_event(self, event_id):
        """
        Deletes an event from the calendar.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            f"""
            DELETE FROM calendar
            WHERE id={event_id}
            """
        )
