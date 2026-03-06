from abc import ABC, abstractmethod
from typing import List, Dict


class BaseVectorStore(ABC):

    @abstractmethod
    def add(self, documents: List[Dict]) -> None:
        """
        documents must contain:
        {
            "id": str,
            "content": str,
            "embedding": List[float],
            "metadata": dict
        }
        """
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict]:
        pass

    @abstractmethod
    def save(self, path: str) -> None:
        pass

    @abstractmethod
    def load(self, path: str) -> None:
        pass