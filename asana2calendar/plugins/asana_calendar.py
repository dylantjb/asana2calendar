"""
asana_calendar.py

This module provides an implementation of the Calendar abstract class for 
interacting with the Asana API.

It defines the AsanaEvent class, which extends the SimpleNamespace class to
represent an event in Asana. It also includes the AsanaCalendar class, which 
implements the Calendar abstract class and provides methods to interact with Asana tasks.

Required Dependencies:
    datetime module from Python standard library
    SimpleNamespace class from the types module from Python standard library
    Client class from the asana package (https://github.com/asana/python-asana)

Example Usage:
    ```
    token = "your_asana_token"
    project_name = "your_project_name"
    calendar = AsanaCalendar(token, project_name)
    start_date = datetime(2022, 3, 1)
    end_date = datetime(2022, 3, 31)
    events = calendar.get_events(start_date, end_date)
    # ... use events ...
    ```
"""

from datetime import datetime
from types import SimpleNamespace

from asana import Client

from asana2calendar.plugins.base_calendar import Calendar


class AsanaEvent(SimpleNamespace):
    """
    Represents an event in Asana with the following attributes:
    - gid (str): globally unique identifier of the task
    - name (str): name of the task
    - location (str): location of the task
    - completed (bool): whether the task is completed or not
    - due_on (datetime): the date and time when the task is due
    - start_on (datetime): the date and time when the task starts
    - modified_on (datetime): the date and time when the task was last modified
    """

    data = ["gid", "name", "location", "completed", "due_on", "start_on", "modified_on"]

    def get_data(self):
        """Returns a dictionary with the task's attributes."""
        return {
            "gid": self.gid,
            "name": self.name,
            "due_on": self.due_on,
            "start_on": self.start_on,
            "modified_on": self.modified_on,
            "completed": self.completed,
        }

    @property
    def due_on(self):
        """Returns the due date of the task as a datetime object."""
        return datetime.strptime(self.due_on, "%Y-%m-%dT%H:%M:%S.%fZ")

    @due_on.setter
    def due_on(self, due_on):
        """Sets the due date of the task to the given datetime object."""
        self.due_on = due_on.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @property
    def start_on(self):
        """Returns the start date of the task as a datetime object."""
        return datetime.strptime(self.start_on, "%Y-%m-%dT%H:%M:%S.%fZ")

    @start_on.setter
    def start_on(self, start_on):
        """Sets the start date of the task to the given datetime object."""
        self.start_on = start_on.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    @property
    def modified_on(self):
        """Returns the date when the task was last modified as a datetime object."""
        return datetime.strptime(self.modified_on, "%Y-%m-%dT%H:%M:%S.%fZ")

    @modified_on.setter
    def modified_on(self, modified_on):
        """Sets the date when the task was last modified to the given datetime object."""
        self.modified_on = modified_on.strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class AsanaCalendar(Calendar):
    """Represents a calendar synchronized with Asana tasks."""

    # pylint: disable=no-member

    def __init__(self, token, name):
        """
        Initializes a new instance of the AsanaCalendar class.

        Args:
            - token (str): The personal access token to authenticate with Asana API.
            - name (str): The name of the project in Asana that contains the tasks to
                          be synchronized with the calendar.
        """
        self._client = Client.access_token(token)
        self._client.headers = {"asana-enable": "new_memberships"}
        self._project_id = self._get_project_id(name)

    def _get_project_id(self, name):
        """Returns the globally unique identifier of the project with the given name."""
        projects = self._client.projects.get_projects(  # type: ignore
            offset=None, iterator_type=None, opt_fields=["name"]
        )  # Paginator disabled without a workspace ID
        return [p for p in projects if p["name"] == name][0]["gid"]

    def get_events(self, start_date, end_date):
        """Returns a list of events between the given start and end dates."""
        return [
            AsanaEvent(**task)
            for task in self._client.tasks.get_tasks_for_project(  # type: ignore
                self._project_id,
                opt_fields=AsanaEvent.data
                + [
                    "sort_by=due_date",
                    f"due_on.after={datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}",
                ],
            )
        ]

    def create_events(self, *events):
        """Creates the given events in the Asana project associated with this calendar."""
        for event in events:
            self._client.tasks.create_task(  # type: ignore
                event.get_data() | {"projects": self._project_id}
            )

    def update_events(self, *events):
        """Updates the given events in the Asana project associated with this calendar."""
        for event in events:
            self._client.tasks.update(event.id, event.get_data())  # type: ignore

    def delete_events(self, *events):
        """Deletes the given events from the Asana project associated with this calendar."""
        for event in events:
            self._client.tasks.delete(event.id)  # type: ignore
