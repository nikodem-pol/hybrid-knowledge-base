from .factory import DBAdapterFactory

class DatabaseConnector:

    def __init__(self, db_type, config):
        self.adapter = DBAdapterFactory.create(db_type)
        self.adapter.connect(config)

    def fetch(self, query):
        return self.adapter.query(query)
    
    def get_db_schema(self):
        return self.adapter.get_schema()
    
    def get_db_schema_with_types(self):
        return self.adapter.get_schema_with_types()

    def close(self):
        self.adapter.close()