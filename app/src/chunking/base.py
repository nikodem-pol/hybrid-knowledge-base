from abc import ABC, abstractmethod
from typing import List, Dict

"""
Chunk schema:
{
    "id": str,
    "content": str,
    "metadata": {
        "source": str,
        "chunk_index": int,
        "start_char": int,
        "end_char": int,
        "type": "file"
    }
}
"""
class BaseChunker(ABC):

    @abstractmethod
    def chunk(self, document: Dict) -> List[Dict]:
        """
            document should be in this format:
            {
                "content": "...",\n
                "metadata": {...}
            }
        """
        pass