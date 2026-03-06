"""
Thin launcher — delegates to the rag package.
Run:  python scripts/rag_ui.py   OR   cd scripts && python -m rag
"""

import sys
import os

# Ensure the scripts directory is on the path so `rag` package is importable
sys.path.insert(0, os.path.dirname(__file__))

from rag.app import RAGApp

if __name__ == "__main__":
    app = RAGApp()
    app.mainloop()
