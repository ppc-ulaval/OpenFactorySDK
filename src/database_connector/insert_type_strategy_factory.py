import json
from insert_type_strategy.interfaces.insert_type_strategy import IInsertTypeStrategy
from insert_type_strategy.strategies.insert_type_float import InsertTypeFloat
from insert_type_strategy.strategies.insert_type_int import InsertTypeInt
from insert_type_strategy.strategies.insert_type_str import InsertTypeStr

class InsertTypeFactory:
    """Factory class to create insert type strategies based on dataitem type"""

    @staticmethod
    def create_strategy(type: str) -> IInsertTypeStrategy:
        """Create an insert type strategy based on provided type."""
        type_convention = {}
        with open('type_convention.json') as f:
            type_convention = json.load(f)
            
        if type in type_convention.get('str'):
            return InsertTypeStr()
        elif type in type_convention.get('int'):
            return InsertTypeInt()
        elif type in type_convention.get('float'):
            return InsertTypeFloat()
