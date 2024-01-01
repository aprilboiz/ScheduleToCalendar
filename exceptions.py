class AuthenticationError(Exception):
    """
    Custom exception class for authentication errors.

    Attributes:
        message (str): The error message.
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ScheduleException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)
