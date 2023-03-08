"""
sync.py - A tool for synchronizing events between multiple calendars.

This file provides a command line interface for synchronizing events between multiple
calendars, including Google Calendar and Microsoft Outlook. It uses the CalDAV protocol
for syncing and SQLAlchemy as the database ORM.

The tool provides the following functionality:
- Two-way syncing of events between multiple calendars
- Support for multiple calendars and events per calendar
- Customizable database creation
- Plugin architecture for extending functionality
"""
class CalendarSync:
    def __init__(self, calendars, conn):
        self.conn = conn
        self.calendars = [c(d) for c, d in calendars]

    def sync(self):
        # Retrieve all events from both calendars
        asana_events = self._get_asana_events()
        calendar_events = self._get_calendar_events()

        # Sync each event in both directions
        for asana_event in asana_events:
            for calendar_event in calendar_events:
                if asana_event["id"] == calendar_event["id"]:
                    self._sync_event(asana_event, calendar_event)

    def _sync_event(self, asana_event, calendar_event):
        # Check which event has a more recent modified_date
        if asana_event["modified_date"] > calendar_event["modified_date"]:
            # Asana event has a more recent modified_date, update the corresponding calendar event
            self._update_calendar_event(
                calendar_event["id"], asana_event["name"], asana_event["modified_date"]
            )
        elif calendar_event["modified_date"] > asana_event["modified_date"]:
            # Calendar event has a more recent modified_date, update the corresponding asana task
            self._update_asana_task(
                asana_event["id"],
                calendar_event["name"],
                calendar_event["modified_date"],
            )

    def _get_asana_events(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM asana")
        return cursor.fetchall()

    def _get_calendar_events(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM calendar")
        return cursor.fetchall()

    def _update_calendar_event(self, event_id, name, modified_date):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE calendar
            SET name=?, modified_date=?
            WHERE id=?
        """,
            (name, modified_date, event_id),
        )
        self.conn.commit()

    def _update_asana_task(self, task_id, name, modified_date):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            UPDATE asana
            SET name=?, modified_date=?
            WHERE id=?
        """,
            (name, modified_date, task_id),
        )
        self.conn.commit()
