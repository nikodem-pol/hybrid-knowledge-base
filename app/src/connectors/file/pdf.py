from .base import BaseFileLoader
import PyPDF2

class PDFLoader(BaseFileLoader):

    def load(self, path):
        text = ""
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
        return text