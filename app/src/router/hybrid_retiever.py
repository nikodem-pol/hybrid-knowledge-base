from .retrieval_startegy_enum import RetrievalStrategy
from sql_generator.utils import format_schema, validate_sql

class HybridRetriever:

    def __init__(
        self,
        db_connector,
        vector_store,
        embedding_model,
        sql_generator,
        router
    ):
        self.db = db_connector
        self.vector = vector_store
        self.embedding = embedding_model
        self.sql_generator = sql_generator
        self.router = router

    def retrieve(self, question: str):

        strategy = self.router.route(question)

        if strategy == RetrievalStrategy.SQL:
            print('====SQL====')
            return self._sql_retrieve(question)

        elif strategy == RetrievalStrategy.VECTOR:
            print('====VECTOR===')
            return self._vector_retrieve(question)

        elif strategy == RetrievalStrategy.HYBRID:
            print('====HYBRID===')
            sql_results = self._sql_retrieve(question)
            vector_results = self._vector_retrieve(question)
            return sql_results + vector_results

    def _sql_retrieve(self, question):
        schema = format_schema(self.db.adapter.get_schema())
        sql = self.sql_generator.generate_sql(question, schema)
        print("SQL: ", sql)
        validate_sql(sql)
        return self.db.fetch(sql)

    def _vector_retrieve(self, question):
        query_embedding = self.embedding.embed_query(question)
        return self.vector.search(query_embedding, top_k=5)