import json
import os
from typing import Dict, List, Literal, Union, Any

from config import TIME_ZONE
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class CalendarResponse:
    """
    Represents a response from Google Calendar API.

    Attributes:
        data (Union[List[Dict[str, str]], Dict[str, str]]): The response data.

    Methods:
        to_json(file_name: str = "response.json"): Save response data to a JSON file.
    """

    def __init__(self, data: Union[List[Dict[str, str]], Dict[str, str]]) -> None:
        self.data = data

    def __str__(self) -> str:
        return str(self.data)

    def to_json(self, file_name: str = "response.json"):
        """
        Save the response data to a JSON file.

        Args:
            file_name (str, optional): The name of the JSON file to save the data to.
                Defaults to "response.json".
        """
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False)
        print(f"File '{file_name}' is saved.")


class Calendar:
    """
    Represents a Google Calendar instance.

    Attributes:
        path (str): The path to the directory containing this module.
        credentials_path (str): The path to the credentials JSON file.
        token_path (str): The path to the token JSON file.
        creds (Credentials): The Google API credentials.
        service (Any): The Google Calendar service.

    Methods:
        __init__(credentials_path: str = "credentials.json", token_path: str = "token.json") -> None: Initialize the Calendar instance.
        get(get_type: Literal["calendars", "events"], name: str = "") -> CalendarResponse: Retrieve calendar data (calendars or events).
        get_calendar_id(name: str) -> Union[str, ValueError]: Get the calendar ID for a given calendar name.
        is_exist(name: str) -> bool: Check if a calendar with a given name exists.
        create_event(events: List[Dict[str, str]], name: str) -> None: Create events in a calendar.
        create_calendar(name: str) -> None: Create a new calendar.
        update_calendar(name: str, new_name: str): Update the name of an existing calendar.
        delete_calendar(name: str): Delete a calendar.
    """

    path = os.path.dirname(os.path.abspath(__file__))

    def __init__(
        self, credentials_path: str = "credentials.json", token_path: str = "token.json"
    ) -> None:
        self.credentials_path: str = f"{self.path}/{credentials_path}"
        self.token_path: str = f"{self.path}/{token_path}"
        self.creds = None
        self.service = None

        self.get_credentials()

        # It literally returns the Resource object with Calendar's methods.
        # Because the Resource object generates methods dynamically.
        # So in this case, static type checking will not work as expected.
        # Using the 'Any' type to compress any errors related to the Resource object.
        self.service: Any = build("calendar", "v3", credentials=self.creds)

    def get_credentials(self):
        # https://developers.google.com/calendar/api/quickstart/python
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except RefreshError:
                    try:
                        os.remove(self.token_path)
                    except FileNotFoundError:
                        pass
                    self.get_credentials()
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())

    def get(self, get_type: Literal["calendars", "events"], name: str = ""):
        """
        Retrieve calendar data (calendars or events).

        Args:
            get_type (Literal["calendars", "events"]): The type of data to retrieve.
            name (str, optional): The name of the calendar (for events). Defaults to "".

        Returns:
            CalendarResponse: An object containing the retrieved data.
        """
        supported_types = ["calendars", "events"]
        page_token = None
        fetch_data: Dict = {}
        result = []

        if get_type not in supported_types:
            raise ValueError(f"'get_type' must be one of {supported_types}")

        if get_type == "calendars":
            fetch_data = (
                self.service.calendarList().list(pageToken=page_token).execute()
            )
        if get_type == "events":
            if name:
                fetch_data = (
                    self.service.events()
                    .list(calendarId=self.get_calendar_id(name), pageToken=page_token)
                    .execute()
                )
            else:
                raise ValueError("You must provide specific calendar name.")

        while True:
            for entry in fetch_data["items"]:
                result.append(entry)
            page_token = fetch_data.get("nextPageToken")
            if not page_token:
                break
        return CalendarResponse(result)

    def get_calendar_id(self, name: str) -> Union[str, ValueError]:
        """
        Get the calendar ID for a given calendar name.

        Args:
            name (str): The name of the calendar.

        Returns:
            Union[str, ValueError]: The calendar ID if found, otherwise raises a ValueError.
        """
        schedule_name = name
        calendar_list = self.get("calendars").data
        if isinstance(calendar_list, List):
            for item in calendar_list:
                if item["summary"] == schedule_name:
                    return item["id"]
        else:
            raise TypeError(f"This type '{type(calendar_list)}' can not be iterable.")
        raise ValueError(
            f"Cannot find '{name}' id. You might need to create a calendar first."
        )

    def is_exist(self, name: str) -> bool:
        """
        Check if a calendar with a given name exists.

        Args:
            name (str): The name of the calendar.

        Returns:
            bool: True if the calendar exists, False otherwise.
        """
        calendar_list = self.get("calendars").data
        if isinstance(calendar_list, List):
            calendar_list = [calendar["summary"] for calendar in calendar_list]
        if name in calendar_list:
            return True
        return False

    def create_event(self, events: List[Dict[str, str]], name: str) -> None:
        """
        Create events in a calendar.

        Args:
            events (List[Dict[str, str]]): A list of event data dictionaries.
            name (str): The name of the calendar to create events in.
        """
        for e in events:
            event = {
                "summary": f'{e["code"]} {e["name"]}',
                "location": f'{e["room"]}',
                "description": f'Class: {e["class"]}\nLecturer: {e["lecturer"]}',
                "start": {
                    "dateTime": f'{e["start_period_date"]}',
                    "timeZone": TIME_ZONE,
                },
                "end": {
                    "dateTime": f'{e["end_period_date"]}',
                    "timeZone": TIME_ZONE,
                },
                "colorId": f'{e["color"]}',
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 30},
                    ],
                },
            }

            # there is no need to repeat one-day events. For example: exam day
            if e["repeat"] and int(e["repeat"]) > 0:
                event["recurrence"] = [f'RRULE:FREQ=WEEKLY;COUNT={e["repeat"]}']

            result = (
                self.service.events()
                .insert(calendarId=self.get_calendar_id(name), body=event)
                .execute()
            )
            print("Inserted %s" % (result["summary"]))

    def create_calendar(self, name: str) -> None:
        """
        Create a new calendar.

        Args:
            name (str): The name of the new calendar.
        """
        # Create SGU Schedule
        calendar = {
            "summary": f"{name}",
            "timeZone": TIME_ZONE,
        }
        created_calendar = self.service.calendars().insert(body=calendar).execute()
        print(f"Created calendar {created_calendar['summary']}.")

    def update_calendar(self, name: str, new_name: str):
        """
        Update the name of an existing calendar.

        Args:
            name (str): The current name of the calendar.
            new_name (str): The new name for the calendar.
        """
        # First retrieve the calendar from the API.
        calendar: Dict = (
            self.service.calendars()
            .get(calendarId=self.get_calendar_id(name))
            .execute()
        )
        calendar["summary"] = new_name
        updated_calendar = (
            self.service.calendars()
            .update(calendarId=calendar["id"], body=calendar)
            .execute()
        )
        print(f"Changed calendar {updated_calendar['summary']}")

    def delete_calendar(self, name: str):
        """
        Delete a calendar.

        Args:
            name (str): The name of the calendar to delete.
        """
        calendar_id = self.get_calendar_id(name)
        self.service.calendars().delete(calendarId=calendar_id).execute()
