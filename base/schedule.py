from abc import ABC, abstractmethod
from .account import Account
from typing import Dict, List


class Schedule(ABC):
    user = Account
    logged_in = bool

    @abstractmethod
    def get_data(self):
        ...

    @abstractmethod
    def standardization(self):
        ...

    def get_semesters(self) -> Dict[str, List[str]]:
        ...
