from typing import List
from sentence_transformers import SentenceTransformer
from .base import BaseEmbeddingAdapter


class SentenceTransformerAdapter(BaseEmbeddingAdapter):

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = None,
        normalize: bool = True
    ):
        self.model = SentenceTransformer(model_name, device=device)
        self.normalize = normalize

    def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=self.normalize,
            show_progress_bar=False
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=self.normalize,
            show_progress_bar=False
        )
        return embedding.tolist()