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
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "ctl00$ContentPlaceHolder1$ctl00$ucDangNhap$txtTaiKhoa": f"{self.username}",
            "ctl00$ContentPlaceHolder1$ctl00$ucDangNhap$txtMatKhau": f"{self.password}",
            "ctl00$ContentPlaceHolder1$ctl00$ucDangNhap$btnDangNhap": "Đăng Nhập",
        }
        res = self.http.post(
            url=constants.BASE_URL + constants.DEFAULT_ENDPOINT,
            data=payload,
        )
        # after the login is successful, the page will be redirected to the home page
        # we will accept this as a sign of successful authentication
        if res.history:
            # get user's name
            soup = BeautifulSoup(res.text, "lxml")
            find_name = soup.find("span", {"id": "ctl00_Header1_Logout1_lblNguoiDung"})
            if find_name is not None:
                self.name = find_name.text

            self.logged_in = not self.logged_in
        else:
            raise AuthenticationError("Login failed.")

    def logout(self):
        """
        Log out from the SGU account.

        Raises:
            AuthenticationError: If the logout fails or if the user is not logged in.
        """
        if self.logged_in is False:
            raise AuthenticationError("User is not logged in.")

        print("Logging out ...")

        payload = {
            "__EVENTTARGET": "ctl00$Header1$Logout1$lbtnLogOut",
            "__EVENTARGUMENT": "",
        }
        res = self.http.post(
            constants.BASE_URL + constants.DEFAULT_ENDPOINT,
            data=payload,
        )
        # check if the user is logged out or not
        res = self.http.get(constants.BASE_URL + constants.SCHEDULE_ENDPOINT)

        # if there is history, it means the user was successfully logged out
        # because of the redirect happened.
        if res.history:
            self.logged_in = not self.logged_in
        else:
            raise AuthenticationError("Logout failed. SessionID: " + self.session_id)
