from base.account import Account
from exceptions import AuthenticationError
from http_request import HttpRequest

from . import constants


class HuflitAccount(Account):
    """
    Represents a Huflit account for authentication and interaction with Huflit's web services.

    Attributes:
        http (HttpRequest): An instance of HttpRequest for making HTTP requests.
        logged_in (bool): A flag indicating whether the user is logged in.
        username (str): The username of the Huflit account.
        password (str): The password of the Huflit account.

    Methods:
        session_id() -> str: Get the ASP.NET_SessionId cookie value.
        login(): Log in to the Huflit account.
        logout(): Log out from the Huflit account.
    """

    def __init__(self, username, password) -> None:
        """
        Initialize a HuflitAccount instance.

        Args:
            username (str): The username of the Huflit account.
            password (str): The password of the Huflit account.
        """
        self.http = HttpRequest()
        self.logged_in = False
        self.username = username
        self.password = password

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
        Log in to the Huflit account.

        Raises:
            AuthenticationError: If the login fails or if the username is blank.
        """
        if not self.username:
            raise AuthenticationError("Username is blank.")

        print("Logging in ...")

        login_url = constants.BASE_URL + constants.LOGIN_ENDPOINT
        payload = {
            "txtTaiKhoan": self.username,
            "txtMatKhau": self.password,
        }
        res = self.http.post(login_url, data=payload)
        # after the login is successful, the page will be redirected to the home page
        # we will accept this as a sign of successful authentication
        if res.history:
            self.logged_in = not self.logged_in
        else:
            raise AuthenticationError("Login failed.")

    def logout(self):
        """
        Log out from the Huflit account.

        Raises:
            AuthenticationError: If the logout fails or if the user is not logged in.
        """
        if self.logged_in is False:
            raise AuthenticationError("User is not logged in.")

        print("Logging out ...")

        logout_url = constants.BASE_URL + constants.LOGOUT_ENDPOINT
        home_url = constants.BASE_URL + constants.HOME_ENDPOINT

        res = self.http.get(logout_url)
        # check if the user is logged out or not
        res = self.http.get(home_url)

        # if there is history, it means the user was successfully logged out
        # because of the redirect happened.
        if res.history:
            self.logged_in = not self.logged_in
        else:
            raise AuthenticationError("Logout failed. SessionID: " + self.session_id)
