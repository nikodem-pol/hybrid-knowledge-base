from .base import BaseChunker
from typing import Dict

class FileIngestionPipeline:

    def __init__(self, chunker: BaseChunker):
        self.chunker = chunker

    def ingest(self, document: Dict):
        return self.chunker.chunk(document)