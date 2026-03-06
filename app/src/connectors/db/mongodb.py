from .base import BaseDBAdapter
from pymongo import MongoClient

class MongoAdapter(BaseDBAdapter):

    def connect(self, config):
        self.client = MongoClient(config["uri"])
        self.db = self.client[config["database"]]

    def query(self, query):
        collection = self.db[query["collection"]]
        return list(collection.find(query.get("filter", {})))

    def close(self):
        self.client.close()