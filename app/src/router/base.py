from .retrieval_startegy_enum import RetrievalStrategy
from abc import ABC, abstractmethod

class BaseRetrievalRouter(ABC):

    @abstractmethod
    def route(self, question: str) -> RetrievalStrategy:
        pass