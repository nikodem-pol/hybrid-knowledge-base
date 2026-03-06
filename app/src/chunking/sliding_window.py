from .base import BaseChunker

import uuid
from typing import List, Dict


class SlidingWindowChunker(BaseChunker):

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 150
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, document: Dict) -> List[Dict]:
        text = document["content"]
        metadata = document.get("metadata", {})
        chunks = []

        start = 0
        chunk_index = 0

        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "id": str(uuid.uuid4()),
                "content": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk_index": chunk_index,
                    "start_char": start,
                    "end_char": end
                }
            })

            start += self.chunk_size - self.chunk_overlap
            chunk_index += 1

        return chunks