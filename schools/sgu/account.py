from bs4 import BeautifulSoup
from base.account import Account
from exceptions import AuthenticationError
from http_request import HttpRequest

from . import constants


class SGUAccount(Account):
    """
    Represents an SGU account for authentication and interaction with SGU's web services.

    Attributes:
        http (HttpRequest): An instance of HttpRequest for making HTTP requests.
        logged_in (bool): A flag indicating whether the user is logged in.
        username (str): The username of the SGU account.
        password (str): The password of the SGU account.
        name (str): The name of the authenticated user.

    Methods:
        session_id() -> str: Get the ASP.NET_SessionId cookie value.
        login(): Log in to the SGU account.
        logout(): Log out from the SGU account.
    """

    def __init__(self, username: str = "", password: str = "") -> None:
        """
        Initialize an SGUAccount instance.

        Args:
            username (str, optional): The username of the SGU account. Defaults to an empty string.
            password (str, optional): The password of the SGU account. Defaults to an empty string.
        """
        self.http = HttpRequest()
        self.logged_in = False
        self.username = username
        self.password = password
        self.name = ""

        self.token_type = ""
        self.access_token = ""

    @property
    def session_id(self) -> str:
        """
        Get the ASP.NET_SessionId cookie value.

        Returns:
            str: The ASP.NET_SessionId cookie value.
        """
        return self.http.session.cookies.get("ASP.NET_SessionId")

    def login(self):
        """
        Log in to the SGU account.

        Raises:
            AuthenticationError: If the login fails or if the username is blank.
        """
        if not self.username:
            raise AuthenticationError("Username is blank.")

        print("Logging in ...")

        payload = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
        }

        res = self.http.post(
            url=constants.BASE_URL + constants.LOGIN_ENDPOINT,
            data=payload,
        )

        res = res.json()

        if int(res["code"]) == 200:
            self.logged_in = not self.logged_in
            self.name = res["name"]

            self.token_type = res["token_type"]
            self.access_token = res["access_token"]
            self.http.headers["Authorization"] = f"{self.token_type} {self.access_token}"

        else:
            raise AuthenticationError(res["message"])

    def logout(self):
        """
        Log out from the SGU account.

        Raises:
            AuthenticationError: If the logout fails or if the user is not logged in.
        """
        if self.logged_in is False:
            raise AuthenticationError("User is not logged in.")

        print("Logging out ...")

        res = self.http.post(
            constants.BASE_URL + constants.LOGOUT_ENDPOINT,
        )

        res = res.json()

        if int(res["code"]) == 200:
            self.logged_in = not self.logged_in
        else:
            raise AuthenticationError("Logout failed. SessionID: " + self.session_id)
