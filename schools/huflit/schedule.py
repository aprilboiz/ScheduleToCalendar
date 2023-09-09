from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Dict, List, Union

from bs4 import BeautifulSoup

from base.schedule import Schedule
from exceptions import AuthenticationError
from schools.huflit.account import HuflitAccount

from . import constants

if TYPE_CHECKING:
    from http_request import HttpRequest


class HUFLITSchedule(Schedule):
    """
    Represents a schedule extractor for HUFLIT.

    Attributes:
        user (HuflitAccount): An instance of HuflitAccount for authentication.

    Methods:
        user_session() -> HttpRequest: Get the user's HTTP session.
        standardization(subject_data: List) -> List[Dict]: Standardize the schedule data.
        get_subject_date(subject: List) -> Dict: Get the start and end dates of a subject.
        get_semesters() -> Dict[str, List[str]]: Get available semesters and years.
        get_data(semester: str, year: str) -> Union[List[Dict], None]: Get schedule data for a specific semester and year.
    """

    def __init__(self, username, password) -> None:
        """
        Initialize an HUFLITSchedule instance.

        Args:
            username (str): The username for the HUFLIT account.
            password (str): The password for the HUFLIT account.
        """
        self.user = HuflitAccount(username, password)

    @property
    def user_session(self) -> "HttpRequest":
        """
        Get the user's HTTP session.

        Returns:
            HttpRequest: The HTTP session of the user.
        """
        return self.user.http

    def standardization(self, subject_data) -> List[Dict[str, str]]:
        """
        Standardize the schedule data.

        Args:
            subject_data (List): The raw schedule data.

        Returns:
            List[Dict]: The standardized schedule data.
        """
        return_data = []
        for subject in subject_data:
            return_data.append(
                {
                    "code": subject[1],
                    "name": subject[2],
                    "credits": subject[3],
                    "class": subject[4],
                    "weekday": subject[5],
                    "start_period": subject[6].split(" - ")[0],
                    "end_period": subject[6].split(" - ")[1],
                    "room": subject[7],
                    "lecturer": subject[8],
                    "from_date": self.get_subject_date(subject)["from_date"],
                    "to_date": self.get_subject_date(subject)["to_date"],
                }
            )
        return return_data

    def get_subject_date(self, subject):
        """
        Get the start and end dates of a subject.

        Args:
            subject (List): The subject data.

        Returns:
            Dict: A dictionary containing "from_date" and "to_date" as ISO-formatted date strings.
        """
        start_period_time = constants.CLASS_TIME[subject[6].split(" - ")[0]]
        period_count = int(subject[6].split(" - ")[1]) - int(subject[6].split(" - ")[0])
        from_date = datetime.strptime(
            f"{subject[9][1:11]} {start_period_time}", "%d/%m/%Y %H:%M:%S"
        )
        to_date = datetime.strptime(
            f"{subject[9][13:-1]} {start_period_time}", "%d/%m/%Y %H:%M:%S"
        )
        to_date += timedelta(days=7, minutes=constants.LESSON_TIME * period_count)

        return {
            "from_date": from_date.isoformat(),
            "to_date": to_date.isoformat(),
        }

    def get_semesters(self) -> Dict[str, List[str]]:
        """
        Get available semesters and years.

        Returns:
            Dict[str, List[str]]: A dictionary containing lists of available semesters and years.
        """
        if self.user.logged_in:
            schedule_url = constants.BASE_URL + constants.SCHEDULE_ENDPOINT
            soup = BeautifulSoup(
                self.user_session.get(schedule_url).text,
                "lxml",
            )
            result_years = soup.find("select", {"id": "YearStudy"})
            result_semesters = soup.find("select", {"id": "TermID"})

            semesters = result_semesters.find_all("option")  # type: ignore
            years = result_years.find_all("option")  # type: ignore
            return {
                "semesters": [semester.attrs["value"] for semester in semesters],
                "years": [year.attrs["value"] for year in years],
            }
        else:
            raise AuthenticationError("User is not logged in.")

    def get_data(self, semester, year) -> Union[List[Dict[str, str]], None]:
        """
        Get schedule data for a specific semester and year.

        Args:
            semester (str): The semester to retrieve schedule data for.
            year (str): The year to retrieve schedule data for.

        Returns:
            Union[List[Dict[str, str]], None]: The schedule data as a list of dictionaries or None if no data is available.
        """
        if self.user.logged_in:
            data = []
            schedule_url = constants.BASE_URL + constants.SCHEDULE_API

            available_semesters = self.get_semesters()
            if (
                year not in available_semesters["years"]
                or semester not in available_semesters["semesters"]
            ):
                raise ValueError(
                    f"The values are invalid. It must be one of {available_semesters}"
                )

            payload = {"YearStudy": year, "TermID": semester}
            response_data = self.user_session.get(schedule_url, params=payload)

            soup = BeautifulSoup(response_data.text, "lxml")
            rows = soup.find_all("tr")
            for row in rows:
                tmp = []
                for col in row.find_all("td"):
                    tmp.append(col.text)
                data.append(tmp)

            data = data[2:]

            if len(data) == 1:
                # 'chua co thoi khoa bieu'
                print(data[0][0])
                return None
            else:
                return self.standardization(data[2:])
        else:
            try:
                self.user.login()
                data = self.get_data(semester, year)
                return data
            finally:
                self.user.logout()
