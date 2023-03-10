"""
caldav_calendar.py

This module provides a wrapper around the caldav library for interacting with CalDAV calendars.
It defines the CaldavCalendar class, which can be used to retrieve, create, update, and delete
events from a CalDAV calendar.

Required Dependencies:
    - caldav (https://github.com/python-caldav/caldav)

Example Usage:
    ```
    from datetime import datetime

    from caldav_calendar import CaldavCalendar

    # Connect to the CalDAV server and log in to the user's account
    client = caldav.DAVClient(<caldav_server_url>, <username>, <password>)
    principal = client.principal()

    calendar = CaldavCalendar(principal)
    # Retrieve events from the user's calendars
    events = calendar.get_events(start_date=datetime(2023, 3, 1), end_date=datetime(2023, 3, 31))

    # Create a new event
    event = {
        "summary": "New event",
        "description": "This is a new event.",
        "location": "Online",
        "start_time": datetime(2023, 3, 15, 10, 0, 0),
        "end_time": datetime(2023, 3, 15, 12, 0, 0),
    }
    calendar.create_event(event)

    # Update an existing event
    event = {
        "id": <event_id>,
        "summary": "Updated event",
        "description": "This event has been updated.",
        "location": "In person",
        "start_time": datetime(2023, 3, 15, 11, 0, 0),
        "end_time": datetime(2023, 3, 15, 13, 0, 0),
    }
    calendar.update_event(event)

    # Delete an existing event
    event_id = <event_id>
    calendar.delete_event(event_id)
    ```
"""
# from caldav.elements import cdav, dav
from datetime import date, datetime

import caldav

from .base import Calendar


class CaldavCalendar(Calendar):
    """The CaldavCalendar class provides an interface to interact with a CalDAV calendar."""

    def __init__(self, principal):
        """Initializes a new instance of the AsanaCalendar class.

        Args:
            principal: caldav.Principal object representing the user's calendar account.
        """
        self.principal = principal
        self.calendars = self.principal.calendars()

    def get_events(
        self, start_date=datetime.now(), end_date=datetime(date.today().year + 1, 1, 1)
    ):
        """Returns a list of events occurring between start_date and end_date."""
        events = []
        for calendar in self.calendars:
            results = calendar.search(
                start=start_date, end=end_date, event=True, expand=True
            )
            for result in results:
                events.append(
                    {
                        "id": result.instance.href,
                        "summary": result.instance.summary,
                        "description": result.instance.description,
                        "location": result.instance.location,
                        "start_time": result.instance.start_time,
                        "end_time": result.instance.end_time,
                        "last_modified": result.instance.last_modified,
                    }
                )
        return events

    def create_event(self, event):
        """Creates an event in the calendar owned by the authenticated user."""
        calendar = self.calendars[0]  # Use the first calendar for simplicity
        vevent = caldav.Event(calendar, event)
        calendar.add_event(vevent)

    def update_event(self, event):
        """Updates an event in the calendar owned by the authenticated user."""
        calendar = self.calendars[0]  # Use the first calendar for simplicity
        event_id = event["id"]
        vevent = calendar.event_by_url(event_id)
        vevent.load()
        vevent.update(event)
        vevent.save()

    def delete_event(self, event_id):
        """
        Deletes an event with the given event_id from the calendar owned by the authenticated user.
        """
        calendar = self.calendars[0]  # Use the first calendar for simplicity
        vevent = calendar.event_by_url(event_id)
        vevent.delete()
