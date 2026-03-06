import faiss
import numpy as np
import pickle
from typing import List, Dict
from .base import BaseVectorStore


class FAISSVectorStore(BaseVectorStore):

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatIP(dimension)  # cosine if normalized
        self.documents = []

    def add(self, documents: List[Dict]) -> None:
        embeddings = np.array(
            [doc["embedding"] for doc in documents],
            dtype="float32"
        )

        self.index.add(embeddings)
        self.documents.extend(documents)

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict]:

        query_vector = np.array([query_embedding], dtype="float32")
        scores, indices = self.index.search(query_vector, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            doc = self.documents[idx]
            results.append({
                **doc,
                "score": float(score)
            })

        return results

    def save(self, path: str) -> None:
        faiss.write_index(self.index, f"{path}/index.faiss")

        with open(f"{path}/documents.pkl", "wb") as f:
            pickle.dump(self.documents, f)

    def load(self, path: str) -> None:
        self.index = faiss.read_index(f"{path}/index.faiss")

        with open(f"{path}/documents.pkl", "rb") as f:
            self.documents = pickle.load(f)