from abc import ABC, abstractmethod
from typing import Any, List, Dict

class BaseDBAdapter(ABC):
    
    @abstractmethod
    def connect(self, config: Dict[str, Any]) -> None:
        pass

    @abstractmethod
    def query(self, query: str) -> List[Dict]:
        pass

    @abstractmethod
    def get_schema(self):
        pass

    @abstractmethod
    def get_schema_with_types(self):
        pass

    @abstractmethod
    def close(self) -> None:
        pass