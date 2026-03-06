from .base import BaseFileLoader


class TXTLoader(BaseFileLoader):
    """
    Loader for plain text files (.txt) and (.md)
    """

    def load(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()