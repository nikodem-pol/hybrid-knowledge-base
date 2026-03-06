from .base import BaseRetrievalRouter
from .retrieval_startegy_enum import RetrievalStrategy


class LLMRetrievalRouter(BaseRetrievalRouter):

    def __init__(self, llm_adapter):
        self.llm = llm_adapter

    def route(self, question: str) -> RetrievalStrategy:

        prompt = f"""
            You are a retrieval strategy classifier.

            Classify the user question into one of:
            - sql (structured database lookup)
            - vector (semantic search in documents)
            - hybrid (requires both structured data and documents)

            Question: {question}

            Return only one word: sql, vector, or hybrid.
            """

        decision = self.llm.generate(prompt).strip().lower()

        return RetrievalStrategy(decision)