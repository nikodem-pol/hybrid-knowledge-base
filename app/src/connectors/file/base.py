from abc import ABC, abstractmethod

class BaseFileLoader(ABC):

    @abstractmethod
    def load(self, path: str) -> str:
        pass