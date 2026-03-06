from dotenv import load_dotenv
import os

from connectors.db.connector import DatabaseConnector
from connectors.file.connector import FileConnector
from connectors.llm.client import LLMClient
from chunking.sentence_aware import SentenceAwareChunker
from chunking.file_ingestion_pipeline import FileIngestionPipeline
from embeddings.factory import EmbeddingFactory
from vector_store.factory import VectorStoreFactory
from router.rule_based_router import RuleBasedRetrievalRouter
from router.hybrid_retiever import HybridRetriever
from sql_generator.llm_sql_generator import LLMSQLGenerator

load_dotenv()

llm_adapter_config = {
    'api_key': os.getenv('llm_api_key')
}

connector = DatabaseConnector('sqlite', {"database": "../../db/mvp.db"})
file_connector = FileConnector()
llm_adapter = LLMClient('openai', **llm_adapter_config)

result = connector.fetch("SELECT COUNT(*) FROM customers;")
text = file_connector.load_file('../../text_files/policies.txt')

router = RuleBasedRetrievalRouter()
sql_generator = LLMSQLGenerator(llm_adapter)
embedding_model = EmbeddingFactory.create(
    "sentence_transformer",
    model_name="all-mpnet-base-v2"
)

raw_text = file_connector.load_file("../../text_files/policies.txt")
document = {
    "content": raw_text,
    "metadata": {"source": "example.txt", "type": "file"}
}
chunker = SentenceAwareChunker(chunk_size=50, chunk_overlap=10)
pipeline = FileIngestionPipeline(chunker)
chunks = pipeline.ingest(document)
texts = [chunk["content"] for chunk in chunks]
vectors = embedding_model.embed(texts)
for chunk, vector in zip(chunks, vectors):
    chunk["embedding"] = vector
embedding_dim = len(chunks[0]["embedding"])

vector_store = VectorStoreFactory.create(
    "faiss",
    dimension=embedding_dim
)
vector_store.add(chunks)

hybrid_retrieval = HybridRetriever(connector, vector_store, embedding_model, sql_generator, router)

while True:
    quesition = input('write your question:')
    print(hybrid_retrieval.retrieve(quesition))

