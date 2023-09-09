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
                    "code": subject[0],
                    "name": subject[1],
                    "credits": subject[3],
                    "class": subject[4].split(", ")[0],
                    "weekday": subject[8],
                    "start_period": subject[9],
                    "end_period": str(int(subject[9]) + int(subject[10])),
                    "room": subject[11],
                    "lecturer": subject[12],
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
        weekday = constants.WEEK_DAY[subject[8]]
        start_period_time = constants.CLASS_TIME[subject[9]]
        period_count = int(subject[10])

        from_date = datetime.strptime(
            f"{semester_start_date} {start_period_time}", "%d/%m/%Y %H:%M:%S"
        )
        to_date = from_date
        to_date += timedelta(
            days=7 * len(subject[13]) + weekday,
            minutes=constants.LESSON_TIME * period_count,
        )

        for c in subject[13]:
            if c.isdigit():
                break
            else:
                from_date += timedelta(days=7)
        from_date += timedelta(days=weekday)

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
        if self.user.logged_in:
            soup = BeautifulSoup(
                self.user_session.get(
                    constants.BASE_URL + constants.SCHEDULE_ENDPOINT
                ).text,
                "lxml",
            )
            result = soup.find(
                "select", {"id": "ctl00_ContentPlaceHolder1_ctl00_ddlChonNHHK"}
            )
            semesters = result.find_all("option")  # type: ignore
            return {"semesters": [semester.attrs["value"] for semester in semesters]}
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

        def get_viewstate():
            soup = BeautifulSoup(
                self.user_session.get(
                    constants.BASE_URL + constants.SCHEDULE_ENDPOINT
                ).text,
                "lxml",
            )
            find_viewstate = soup.find("input", {"id": "__VIEWSTATE"})
            return (
                find_viewstate.attrs["value"]  # type: ignore
                if find_viewstate is not None
                else find_viewstate
            )

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
            self.semester = semester

            data = []
            payload = {
                "__EVENTTARGET": "ctl00$ContentPlaceHolder1$ctl00$rad_ThuTiet",
                "__EVENTARGUMENT": "",
                "__LASTFOCUS": "",
                "__VIEWSTATE": get_viewstate(),
                "ctl00$ContentPlaceHolder1$ctl00$ddlChonNHHK": semester,
                "ctl00$ContentPlaceHolder1$ctl00$ddlLoai": "1",
                "ctl00$ContentPlaceHolder1$ctl00$rad_ThuTiet": "rad_ThuTiet",
                "ctl00$ContentPlaceHolder1$ctl00$rad_MonHoc": "rad_MonHoc",
            }

            response = self.user_session.post(
                constants.BASE_URL + constants.SCHEDULE_ENDPOINT,
                data=payload,
            )
            # extract data from response
            soup = BeautifulSoup(response.text, "lxml")
            rows = soup.find_all("tr", {"height": "22px"})

            # extract text from each row
            for row in rows:
                tmp_data = []
                for td in row.find_all("td"):
                    tmp_data.append(td.text)
                data.append(tmp_data)

            if len(data) == 0:
                return None

            return self.standardization(data)
        else:
            try:
                print("User is not logged in. Trying to login...")
                self.user.login()
                data = self.get_data(semester)
                return data
            finally:
                self.user.logout()
