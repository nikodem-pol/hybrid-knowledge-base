"""
Chat tab: message bubbles, suggestion chips, auto-scroll.
"""

import customtkinter as ctk
from .config import COLORS


class ChatTab:
    """Builds and manages the Chat tab inside a CTkTabview tab frame."""

    def __init__(self, parent: ctk.CTkFrame, app):
        """
        Parameters
        ----------
        parent : the tab frame returned by tabview.add("Chat")
        app    : the RAGApp instance (for accessing shared state + sidebar)
        """
        self.app = app
        self.chat_history: list[dict] = []

        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        ctk.CTkLabel(
            header, text="Ask your knowledge base",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Questions are answered using both uploaded files and connected databases.",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        # Scrollable chat area
        self.chat_scroll = ctk.CTkScrollableFrame(
            parent, fg_color=COLORS["bg_panel"], corner_radius=12,
        )
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        self._placeholder = ctk.CTkLabel(
            self.chat_scroll,
            text=(
                "\n\nYour knowledge base is ready\n\n"
                "Upload files or connect databases, then ask questions here."
            ),
            font=ctk.CTkFont(size=14), text_color=COLORS["text_muted"], wraplength=400,
        )
        self._placeholder.grid(row=0, column=0, pady=80)

        # Input row
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 4))
        input_frame.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask a question about your knowledge base...",
            height=42, font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
        )
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry.bind("<Return>", lambda _: self._send())

        ctk.CTkButton(
            input_frame, text="Send", width=80, height=42,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=self._send,
        ).grid(row=0, column=1)

        # Suggestion chips
        chip_frame = ctk.CTkFrame(parent, fg_color="transparent")
        chip_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))

        for s in [
            "Summarize all documents",
            "What tables exist in my DB?",
            "Compare files & DB sources",
            "List key entities in my data",
        ]:
            ctk.CTkButton(
                chip_frame, text=s, height=30, font=ctk.CTkFont(size=11),
                fg_color=COLORS["bg_card"], hover_color=COLORS["bg_input"],
                text_color=COLORS["text_secondary"], corner_radius=16,
                command=lambda q=s: self._send_suggestion(q),
            ).pack(side="left", padx=(0, 6))

    # ── actions ──────────────────────────────────────────────────────────────
    def _send_suggestion(self, text: str):
        self.entry.delete(0, "end")
        self.entry.insert(0, text)
        self._send()

    def _send(self):
        query = self.entry.get().strip()
        if not query:
            return
        self.entry.delete(0, "end")
        self._placeholder.grid_forget()

        self.chat_history.append({"role": "user", "content": query})
        self._bubble(query, is_user=True)

        # ── placeholder response (wire your RAG pipeline here) ──
        sb = self.app.sidebar
        nf = len(self.app.uploaded_files)
        nd = len(self.app.db_connections)
        response = (
            f"[Placeholder response]\n\n"
            f"Your question \"{query}\" would be answered by:\n"
            f"1. Embedding the query with {sb.embed_var.get()}\n"
            f"2. Retrieving top-{sb.topk_entry.get()} chunks from {nf} file(s) "
            f"and querying {nd} database(s)\n"
            f"3. Generating with {sb.provider_var.get()} / {sb.model_var.get()}\n\n"
            f"Connect your RAG backend to replace this stub."
        )
        sources = [f["name"] for f in self.app.uploaded_files[:2]]
        sources += [c["name"] for c in self.app.db_connections[:1]]
        if not sources:
            sources = ["No sources loaded yet"]

        self.chat_history.append({"role": "assistant", "content": response, "sources": sources})
        self._bubble(response, is_user=False, sources=sources)

    def _bubble(self, text: str, is_user: bool = True, sources: list[str] | None = None):
        row = len(self.chat_history) - 1

        outer = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        outer.grid(row=row, column=0, sticky="e" if is_user else "w", padx=8, pady=4)

        bubble = ctk.CTkFrame(
            outer,
            fg_color=COLORS["user_bubble"] if is_user else COLORS["assistant_bubble"],
            corner_radius=16,
        )
        bubble.pack(anchor="e" if is_user else "w")

        ctk.CTkLabel(
            bubble, text=text, wraplength=520, justify="left",
            font=ctk.CTkFont(size=13),
            text_color="#ffffff" if is_user else COLORS["text_primary"],
        ).pack(padx=14, pady=10)

        if sources and not is_user:
            ctk.CTkLabel(
                bubble, text="Sources: " + " | ".join(sources),
                font=ctk.CTkFont(size=10), text_color=COLORS["text_muted"],
                wraplength=520, justify="left",
            ).pack(padx=14, pady=(0, 8))

        self.chat_scroll._parent_canvas.yview_moveto(1.0)
