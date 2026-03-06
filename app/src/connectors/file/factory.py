from .html import HTMLLoader
from .txt import TXTLoader
from .pdf import PDFLoader


class FileLoaderFactory:

    LOADERS = {
        ".pdf": PDFLoader,
        ".md": TXTLoader,
        ".html": HTMLLoader,
        ".txt": TXTLoader,
    }

    @classmethod
    def create(cls, file_extension):
        loader = cls.LOADERS.get(file_extension)
        if not loader:
            raise ValueError("Unsupported file type")
        return loader()