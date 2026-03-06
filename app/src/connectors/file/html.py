from bs4 import BeautifulSoup
from .base import BaseFileLoader

class HTMLLoader(BaseFileLoader):

    def load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, "html.parser")
            return soup.get_text()