from .base import BaseChunker
from typing import List, Dict
import re
import uuid

class SentenceAwareChunker(BaseChunker):

    def __init__(self, chunk_size=800, chunk_overlap=150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_sentences(self, text: str):
        return re.split(r'(?<=[.!?])\s+', text)

    def chunk(self, document: Dict) -> List[Dict]:
        sentences = self.split_sentences(document["content"])
        metadata = document.get("metadata", {})

        chunks = []
        current_chunk = ""
        chunk_index = 0

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < self.chunk_size:
                current_chunk += sentence + " "
            else:
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "content": current_chunk.strip(),
                    "metadata": {
                        **metadata,
                        "chunk_index": chunk_index
                    }
                })

                chunk_index += 1
                current_chunk = sentence + " "

        if current_chunk:
            chunks.append({
                "id": str(uuid.uuid4()),
                "content": current_chunk.strip(),
                "metadata": {
                    **metadata,
                    "chunk_index": chunk_index
                }
            })

        return chunks