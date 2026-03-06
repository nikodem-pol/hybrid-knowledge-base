from abc import ABC, abstractmethod

class BaseLLMAdapter(ABC):

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass