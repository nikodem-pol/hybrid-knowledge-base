"""
Entry point: python -m rag
"""

from .app import RAGApp


def main():
    app = RAGApp()
    app.mainloop()


if __name__ == "__main__":
    main()
