from abc import ABC, abstractmethod


class BaseSQLGenerator(ABC):

    @abstractmethod
    def generate_sql(self, question: str, schema: str) -> str:
        pass