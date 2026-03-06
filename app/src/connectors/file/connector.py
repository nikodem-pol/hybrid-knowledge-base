from .factory import FileLoaderFactory
import os

class FileConnector:

    def load_file(self, path):
        ext = os.path.splitext(path)[1]
        loader = FileLoaderFactory.create(ext)
        return loader.load(path)