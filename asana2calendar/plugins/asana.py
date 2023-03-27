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

import os
import sys
import webbrowser
from datetime import date, datetime
from types import SimpleNamespace

from asana import Client

from .base import Calendar


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


class AsanaCalendar:
    """Represents a calendar synchronized with Asana tasks."""

    URL = "https://auth.dylantjb.com"

    # pylint: disable=no-member

    def __init__(self, **token):
        """
        Initializes a new instance of the AsanaCalendar class.

        Args:
            - token (str): The personal access token to authenticate with Asana API.
        """
        self._client = Client.oauth(
            client_id=1204150703591373,
            token=self._get_token(token),
        )
        self._client.headers = {"asana-enable": "new_memberships"}
        if os.environ.get("PROJECT"):
            self._project_id = self._get_project_id(os.environ["PROJECT"])

    @staticmethod
    def _get_token(token):
        if not token:

        else:
            client = Client.oauth(
                client_id="1204150703591373",
                client_secret="f34d55b1213adb6c3e34d76b8d116b2b",
                redirect_uri="urn:ietf:wg:oauth:2.0:oob",
            )

            url, _ = client.session.authorization_url()
            try:
                webbrowser.open(url)
            except webbrowser.Error:
                print("Open the following URL in a browser to authorize:")
                print(url)
            code = input(
                "Copy and paste the returned code from the browser and press enter: "
            )
            cls.TOKEN = client.session.fetch_token(code=code)
            return client

    def showinfo(self):
        info = self._client.users.get_user("me")
        print(f'gid: {info["gid"]}')
        print(f'name: {info["name"]}')
        print(f'email: {info["email"]}')

    @staticmethod
    def convert_to_datetime(string):
        return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ")

    @staticmethod
    def convert_to_datestring(time):
        return time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    def _get_project_id(self, name):
        """Returns the globally unique identifier of the project with the given name."""
        projects = self._client.projects.get_projects(  # type: ignore
            offset=None, iterator_type=None, opt_fields=["name"]
        )  # Paginator disabled without a workspace ID
        return [p for p in projects if p["name"] == name][0]["gid"]

    def get_events(
        self,
        start_date=datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        end_date=datetime(date.today().year + 1, 1, 1),
    ):
        """Returns a list of events between the given start and end dates."""
        return [
            AsanaEvent(**task)
            for task in self._client.tasks.get_tasks_for_project(  # type: ignore
                self._project_id,
                opt_fields=AsanaEvent.data
                + [
                    f"due_on.after={self.convert_to_datestring(start_date)}",
                    f"due_on.before={self.convert_to_datestring(end_date)}",
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
