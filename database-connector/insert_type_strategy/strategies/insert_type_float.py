from insert_type_strategy.interfaces.insert_type_strategy import IInsertTypeStrategy
from pyodbc import Connection

class InsertTypeFloat(IInsertTypeStrategy):
    """Inserts str values into StrValue table."""

    def insert_value(self, connection: Connection, variable_id: str, update_value: float, update_timestamp: str):
        "Insert new value for a variable"
        try:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO FloatValue (VariableId, Value, Timestamp) VALUES (?, ?, ?)",
                           (variable_id, update_value, update_timestamp))
            cursor.commit()
            cursor.close()
        except Exception as e:
            print(f"Error updating variable {variable_id}: {e}")