from enum import Enum


class RetrievalStrategy(Enum):
    SQL = "sql"
    VECTOR = "vector"
    HYBRID = "hybrid"