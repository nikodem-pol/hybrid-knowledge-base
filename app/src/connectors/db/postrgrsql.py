from .base import BaseDBAdapter
import psycopg2

class PostgresAdapter(BaseDBAdapter):

    def connect(self, config):
        self.conn = psycopg2.connect(**config)
        self.cursor = self.conn.cursor()

    def query(self, query):
        self.cursor.execute(query)
        columns = [desc[0] for desc in self.cursor.description]
        rows = self.cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]

    def close(self):
        self.cursor.close()
        self.conn.close()