from .sentence_transformer_adapter import SentenceTransformerAdapter


class EmbeddingFactory:

    PROVIDERS = {
        "sentence_transformer": SentenceTransformerAdapter
    }

    @classmethod
    def create(cls, provider: str, **config):
        adapter = cls.PROVIDERS.get(provider)
        if not adapter:
            raise ValueError(f"Unsupported embedding provider: {provider}")
        return adapter(**config)