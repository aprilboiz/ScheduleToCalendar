from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Dict, List, Union
from bs4 import BeautifulSoup
from base.schedule import Schedule
from exceptions import AuthenticationError
from schools.sgu.account import SGUAccount

from . import constants

if TYPE_CHECKING:
    from http_request import HttpRequest


class SGUSchedule(Schedule):
    """
    Extract schedule data from SGU website.
    This class is a part of my attempt to get schedule data from SGU to Google Calendar.
    It's used to extract schedule data from SGU website.

    Args:
        username (str): The username for SGU account.
        password (str): The password for SGU account.

    Methods:
        get_semester() -> Dict[str, List[str]]: Get available semesters.
        standardization(subject_data) -> List[Dict[str, str]]: Standardize subject data.
        get_subject_date(subject) -> Dict[str, str]: Get subject date range.
        get_data(semester: str = "") -> Union[List[Dict[str, str]], None]: Get schedule data for a specific semester.

    Returns:
        data (List[List[str, str]]): A list of standardized schedule data.

    Easiest way to get schedule data:
    ```python
    schedule_data = SGUSchedule(username, password).get_data(semester)
    ```

    Or you can use:
    ```python
    schedule = SGUSchedule(username, password)
    schedule.user.login()
    data = schedule.get_data(semester)
    schedule.user.logout()
    ```

    Logging out is recommended after getting schedule data.
    """

    def __init__(self, username: str = "", password: str = "") -> None:
        """
        Initialize an SGUSchedule instance.

        Args:
            username (str, optional): The username for SGU account. Defaults to an empty string.
            password (str, optional): The password for SGU account. Defaults to an empty string.
        """
        self.user = SGUAccount(username, password)
        self.semester = ""
        self.lecturers = []

    @property
    def user_session(self) -> "HttpRequest":
        return self.user.http

    def standardization(self, subject_data) -> List[Dict[str, str]]:
        """
        Standardize the subject data extracted from the website.

        Args:
            subject_data: The raw subject data.

        Returns:
            List[Dict[str, str]]: The standardized subject data.
        """
        return_data = []
        for subject in subject_data:
            return_data.append(
                {
                    "code": subject['ma_mon'],
                    "name": subject['ten_mon'],
                    "credits": subject['so_tc'],
                    "class": subject['lop'],
                    "weekday": subject['thu'],
                    "start_period": subject['tbd'],
                    "end_period": str(int(subject['tbd']) + int(subject['so_tiet'])),
                    "room": subject['phong'],
                    "lecturer": subject['gv'],
                    "from_date": self.get_subject_date(subject)["from_date"],
                    "to_date": self.get_subject_date(subject)["to_date"],
                }
            )
        return return_data

    def get_subject_date(self, subject) -> Dict[str, str]:
        """
        Get the date range for a subject.

        Args:
            subject: The subject data.

        Returns:
            Dict[str, str]: A dictionary containing 'from_date' and 'to_date'.
        """
        semester_start_date = constants.SEMESTER_DATE[self.semester]
        weekday = constants.WEEK_DAY[str(subject['thu'])]
        start_period_time = constants.CLASS_TIME[str(subject['tbd'])]
        period_count = int(subject['so_tiet'])

        from_date = datetime.strptime(
            f"{semester_start_date} {start_period_time}", "%d/%m/%Y %H:%M:%S"
        )

        for c in subject['tkb']:
            if c.isdigit():
                break
            else:
                from_date += timedelta(days=7)
        from_date += timedelta(days=weekday)

        to_date = from_date
        to_date += timedelta(
            days=7 * len(subject['tkb'].replace("-", "")),
            minutes=constants.LESSON_TIME * period_count,
        )

        return {
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
        }

    def get_semesters(self) -> Dict[str, List[str]]:
        """
        Get available semesters.

        Returns:
            Dict[str, List[str]]: A dictionary containing 'semesters'.
        """
        semesters = []
        if self.user.logged_in:

            res = self.user_session.post(constants.BASE_URL + constants.SCHEDULE_LIST_ENDPOINT)

            if res.status_code == 200:
                res = res.json()
                semesters = res["data"]["ds_hoc_ky"]

            return {"semesters": [semester["hoc_ky"] for semester in semesters]}
        else:
            raise AuthenticationError("User is not logged in.")

    def get_data(self, semester: str = "") -> Union[List[Dict[str, str]], None]:
        """
        Get schedule data for a specific semester.

        Args:
            semester (str, optional): The semester for which to get the schedule data. Defaults to an empty string.

        Returns:
            Union[List[Dict[str, str]], None]: A list of standardized schedule data, or None if no data is available.

        Raises:
            AuthenticationError: If the user is not logged in.
            ValueError: If the provided semester is invalid.
        """

        if self.user.logged_in:
            if not semester:
                semester = self.get_semesters()["semesters"][0]
                print(
                    "Semester not found. Class schedule will be taken from this semester:",
                    semester,
                )
            else:
                available_semesters = self.get_semesters()["semesters"]
                if semester not in available_semesters:
                    raise ValueError(
                        f"The semester is invalid. It must be one of {available_semesters}"
                    )
            self.semester = str(semester)

            data = []
            payload = {
                "hoc_ky": self.semester,
                "id_du_lieu": None,
                "loai_doi_tuong": 1
            }

            response = self.user_session.post(
                constants.BASE_URL + constants.SCHEDULE_ENDPOINT,
                data=payload,
            )

            if response.status_code == 200:
                res = response.json()

                # check if that semester has a schedule or not
                if res['data']['total_items'] != 0:
                    data = res['data']['ds_nhom_to']

            return self.standardization(data)
        else:
            try:
                print("User is not logged in. Trying to login...")
                self.user.login()
                data = self.get_data(semester)
                return data
            finally:
                self.user.logout()
