from abc import ABC, abstractmethod


class Account(ABC):
    """
    This is an abstract class for user account.
    You need to implement these properties:
    logged_in: bool
    username: str
    password: str
    name: str
    http(optional): HttpRequest
    """

    @abstractmethod
    def login(self):
        ...

    @abstractmethod
    def logout(self):
        ...
