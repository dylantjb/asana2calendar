"""
calendar.py - This module provides an abstract base class for implementing calendar objects.

The Calendar class provides a blueprint for creating calendar objects that can be used to represent
various types of calendars (e.g., CalDav, Asana). The class defines a number of
abstract methods that must be implemented by any concrete subclass, including methods for getting
and updating, adding, and deleting events.

Example Usage:

    class CaldavCalendar(Calendar):
        # Implement the abstract methods of the Calendar class here...

    calendar = CaldavCalendar(principal)
    start_date = datetime(2022, 3, 1)
    end_date = datetime(2022, 3, 31)
    events = calendar.get_events(start_date, end_date)
    # ... use events ...
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class Calendar(ABC):
    """
    Abstract class representing a calendar.

    This class defines the interface for a calendar that can be used to retrieve and modify events.

    Methods:
        get_events(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
            Retrieves a list of events between the specified start and end dates.

        add_event(event: Dict[str, Any]) -> str:
            Adds the specified event to the calendar and returns the unique identifier of the event.

        update_event(event_id: str, event: Dict[str, Any]) -> None:
            Updates the specified event with the provided data.

        delete_event(event_id: str) -> None:
            Deletes the specified event from the calendar.
    """

    @abstractmethod
    def get_events(self, start_date, end_date) -> List[Dict[str, Any]]:
        """Retrieves a list of events between the specified start and end dates."""

    @abstractmethod
    def create_event(self, *events) -> str:
        """Add an event to the calendar and returns the unique identifier of the event."""

    @abstractmethod
    def update_event(self, *events) -> None:
        """Updates the specified event with the provided data."""

    @abstractmethod
    def delete_event(self, event_id) -> None:
        """Deletes the specified event from the calendar."""
