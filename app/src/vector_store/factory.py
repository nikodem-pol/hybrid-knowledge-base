from .faiss_store import FAISSVectorStore

class VectorStoreFactory:

    STORES = {
        "faiss": FAISSVectorStore
    }

    @classmethod
    def create(cls, store_type: str, **config):
        store = cls.STORES.get(store_type)
        if not store:
            raise ValueError(f"Unsupported vector store: {store_type}")
        return store(**config)