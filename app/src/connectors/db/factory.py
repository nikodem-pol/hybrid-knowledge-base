from .mongodb import MongoAdapter
from .postrgrsql import PostgresAdapter
from .sqlite import SQLiteAdapter

class DBAdapterFactory:

    ADAPTERS = {
        "postgres": PostgresAdapter,
        "mongo": MongoAdapter,
        "sqlite": SQLiteAdapter
    }

    @classmethod
    def create(cls, db_type: str):
        adapter = cls.ADAPTERS.get(db_type)
        if not adapter:
            raise ValueError(f"Unsupported DB type: {db_type}")
        return adapter()