from abc import ABC, abstractmethod
from pyodbc import Connection


class IInsertTypeStrategy(ABC):
    """Abstract base class for different value insert strategies"""

    @abstractmethod
    def insert_value(self, connection: Connection, variable_id: str, update_value: int, update_timestamp: str):
        "Insert new value for a variable"
        pass