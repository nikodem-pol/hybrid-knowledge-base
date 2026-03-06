from .base import BaseRetrievalRouter
from .retrieval_startegy_enum import RetrievalStrategy
import re
from typing import Optional


class RuleBasedRetrievalRouter(BaseRetrievalRouter):

    SQL_KEYWORDS = [
        "count",
        "how many",
        "number of",
        "total",
        "sum",
        "average",
        "avg",
        "max",
        "min",
        "list all",
        "show all",
        "group by",
        "per",
        "between",
        "before",
        "after"
    ]

    VECTOR_KEYWORDS = [
        "explain",
        "describe",
        "what is",
        "why",
        "how does",
        "policy",
        "guidelines",
        "documentation",
        "meaning",
        "definition"
    ]

    NUMERIC_PATTERN = re.compile(r"\d+")

    def route(self, question: str) -> RetrievalStrategy:
        question_lower = question.lower()

        sql_score = 0
        vector_score = 0

        # Keyword scoring
        for keyword in self.SQL_KEYWORDS:
            if keyword in question_lower:
                sql_score += 1

        for keyword in self.VECTOR_KEYWORDS:
            if keyword in question_lower:
                vector_score += 1

        # Numeric pattern boost
        if self.NUMERIC_PATTERN.search(question_lower):
            sql_score += 1

        # Aggregation detection
        if any(word in question_lower for word in ["per ", " by ", "group"]):
            sql_score += 1

        # Decision logic
        if sql_score > 0 and vector_score == 0:
            return RetrievalStrategy.SQL

        if vector_score > 0 and sql_score == 0:
            return RetrievalStrategy.VECTOR

        if sql_score > 0 and vector_score > 0:
            return RetrievalStrategy.HYBRID

        # Default fallback
        return RetrievalStrategy.VECTOR