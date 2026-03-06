"""
Hybrid RAG Knowledge Base — Desktop UI (CustomTkinter)
======================================================
Run:  python scripts/rag_ui.py
Deps: pip install customtkinter
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import hashlib
import os
from datetime import datetime

# ── Theme ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg_dark": "#0f172a",
    "bg_panel": "#1e293b",
    "bg_card": "#273548",
    "bg_input": "#334155",
    "accent": "#3b82f6",
    "accent_hover": "#2563eb",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "error": "#ef4444",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "border": "#334155",
    "user_bubble": "#3b82f6",
    "assistant_bubble": "#273548",
}

SUPPORTED_EXTENSIONS = [
    ("All Supported", "*.pdf *.txt *.md *.html *.htm *.csv *.json *.xml *.docx *.rst *.log"),
    ("PDF", "*.pdf"), ("Text", "*.txt"), ("Markdown", "*.md"),
    ("HTML", "*.html *.htm"), ("CSV", "*.csv"), ("JSON", "*.json"),
    ("XML", "*.xml"), ("DOCX", "*.docx"), ("RST", "*.rst"), ("Log", "*.log"),
]

LLM_MODELS = {
    "OpenAI":    ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1-preview", "o1-mini"],
    "Anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-3.5-sonnet"],
    "Google":    ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
    "Mistral":   ["mistral-large", "mistral-medium", "mistral-small", "mixtral-8x7b"],
    "Groq":      ["llama-3-70b", "llama-3-8b", "mixtral-8x7b", "gemma-7b"],
    "Local / Ollama": ["llama3", "mistral", "phi3", "gemma", "codellama", "custom"],
}

EMBEDDING_MODELS = [
    "text-embedding-3-small", "text-embedding-3-large",
    "text-embedding-ada-002", "all-MiniLM-L6-v2 (local)", "nomic-embed-text (local)",
]


def file_id(name: str, size: int) -> str:
    return hashlib.md5(f"{name}{size}".encode()).hexdigest()[:10]


def format_size(b: int) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {u}"
        b /= 1024
    return f"{b:.1f} TB"


# ═════════════════════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ═════════════════════════════════════════════════════════════════════════════
class RAGApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RAG Knowledge Base")
        self.geometry("1280x820")
        self.minsize(960, 640)
        self.configure(fg_color=COLORS["bg_dark"])

        # ── State ──
        self.uploaded_files: list[dict] = []
        self.db_connections: list[dict] = []
        self.chat_history: list[dict] = []
        self.indexing_status: dict[str, str] = {}

        # ── Layout: sidebar + main ──
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main()

    # ─────────────────────────────────────────────────────────────────────────
    #  SIDEBAR
    # ─────────────────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color=COLORS["bg_panel"])
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        pad = {"padx": 16, "pady": (0, 0)}

        # ── Title ──
        ctk.CTkLabel(
            self.sidebar, text="RAG Knowledge Base",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=COLORS["text_primary"],
        ).pack(padx=16, pady=(20, 2), anchor="w")
        ctk.CTkLabel(
            self.sidebar, text="Hybrid retrieval from files & databases",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"],
        ).pack(padx=16, pady=(0, 12), anchor="w")

        self._sidebar_sep()

        # ── LLM CONFIG ──
        self._section_label("LLM CONFIGURATION")

        ctk.CTkLabel(self.sidebar, text="Provider", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(**pad, anchor="w")
        self.provider_var = ctk.StringVar(value="OpenAI")
        self.provider_menu = ctk.CTkOptionMenu(
            self.sidebar, variable=self.provider_var, values=list(LLM_MODELS.keys()),
            command=self._on_provider_change, fg_color=COLORS["bg_input"],
            button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"],
        )
        self.provider_menu.pack(padx=16, pady=(2, 8), fill="x")

        ctk.CTkLabel(self.sidebar, text="Model", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(**pad, anchor="w")
        self.model_var = ctk.StringVar(value="gpt-4o")
        self.model_menu = ctk.CTkOptionMenu(
            self.sidebar, variable=self.model_var, values=LLM_MODELS["OpenAI"],
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
        )
        self.model_menu.pack(padx=16, pady=(2, 8), fill="x")

        ctk.CTkLabel(self.sidebar, text="API Key", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(**pad, anchor="w")
        self.api_key_entry = ctk.CTkEntry(
            self.sidebar, placeholder_text="sk-...", show="*",
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
        )
        self.api_key_entry.pack(padx=16, pady=(2, 8), fill="x")

        # ── Advanced toggle ──
        self.adv_visible = False
        self.adv_toggle_btn = ctk.CTkButton(
            self.sidebar, text="Advanced Settings  +", font=ctk.CTkFont(size=11),
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"], anchor="w",
            command=self._toggle_advanced,
        )
        self.adv_toggle_btn.pack(padx=16, pady=(0, 4), fill="x")

        self.adv_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        # not packed yet

        # Temperature
        ctk.CTkLabel(self.adv_frame, text="Temperature", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(padx=0, anchor="w")
        self.temp_slider = ctk.CTkSlider(self.adv_frame, from_=0, to=1, number_of_steps=20,
                                          button_color=COLORS["accent"],
                                          button_hover_color=COLORS["accent_hover"])
        self.temp_slider.set(0.2)
        self.temp_slider.pack(fill="x", pady=(2, 6))

        # Top-K
        ctk.CTkLabel(self.adv_frame, text="Top-K Chunks", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.topk_entry = ctk.CTkEntry(self.adv_frame, fg_color=COLORS["bg_input"],
                                        border_color=COLORS["border"])
        self.topk_entry.insert(0, "5")
        self.topk_entry.pack(fill="x", pady=(2, 6))

        # Chunk size
        ctk.CTkLabel(self.adv_frame, text="Chunk Size (tokens)", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.chunk_entry = ctk.CTkEntry(self.adv_frame, fg_color=COLORS["bg_input"],
                                         border_color=COLORS["border"])
        self.chunk_entry.insert(0, "512")
        self.chunk_entry.pack(fill="x", pady=(2, 6))

        # Embedding model
        ctk.CTkLabel(self.adv_frame, text="Embedding Model", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.embed_var = ctk.StringVar(value=EMBEDDING_MODELS[0])
        ctk.CTkOptionMenu(
            self.adv_frame, variable=self.embed_var, values=EMBEDDING_MODELS,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
        ).pack(fill="x", pady=(2, 6))

        self._sidebar_sep()

        # ── Stats ──
        self._section_label("KNOWLEDGE BASE")
        self.stats_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.stats_frame.pack(padx=16, fill="x", pady=(0, 8))
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.stat_files = self._stat_card(self.stats_frame, "0", "Files", 0)
        self.stat_dbs = self._stat_card(self.stats_frame, "0", "DBs", 1)
        self.stat_indexed = self._stat_card(self.stats_frame, "0", "Indexed", 2)

        # ── Status label ──
        self.status_label = ctk.CTkLabel(
            self.sidebar, text="  API key not set", font=ctk.CTkFont(size=12),
            text_color=COLORS["warning"], anchor="w",
        )
        self.status_label.pack(padx=16, pady=(4, 8), anchor="w")

        self.api_key_entry.bind("<KeyRelease>", self._on_key_change)

        self._sidebar_sep()
        ctk.CTkLabel(
            self.sidebar, text="v0.1.0  |  Hybrid RAG UI",
            font=ctk.CTkFont(size=10), text_color=COLORS["text_muted"],
        ).pack(padx=16, pady=(4, 16), anchor="w")

    def _stat_card(self, parent, value, label, col):
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=8)
        frame.grid(row=0, column=col, padx=3, sticky="ew")
        val_lbl = ctk.CTkLabel(frame, text=value, font=ctk.CTkFont(size=20, weight="bold"),
                                text_color=COLORS["text_primary"])
        val_lbl.pack(pady=(8, 0))
        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=9),
                      text_color=COLORS["text_muted"]).pack(pady=(0, 8))
        return val_lbl

    def _section_label(self, text):
        ctk.CTkLabel(
            self.sidebar, text=text,
            font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_muted"],
        ).pack(padx=16, pady=(8, 4), anchor="w")

    def _sidebar_sep(self):
        ctk.CTkFrame(self.sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=16, pady=8)

    def _toggle_advanced(self):
        self.adv_visible = not self.adv_visible
        if self.adv_visible:
            self.adv_frame.pack(padx=16, fill="x", after=self.adv_toggle_btn)
            self.adv_toggle_btn.configure(text="Advanced Settings  -")
        else:
            self.adv_frame.pack_forget()
            self.adv_toggle_btn.configure(text="Advanced Settings  +")

    def _on_provider_change(self, choice):
        models = LLM_MODELS.get(choice, [])
        self.model_menu.configure(values=models)
        self.model_var.set(models[0] if models else "")
        if choice == "Local / Ollama":
            self.api_key_entry.configure(show="", placeholder_text="http://localhost:11434")
        else:
            self.api_key_entry.configure(show="*", placeholder_text="sk-...")

    def _on_key_change(self, _event=None):
        key = self.api_key_entry.get().strip()
        if key:
            p = self.provider_var.get()
            m = self.model_var.get()
            self.status_label.configure(text=f"  {p} connected  |  {m}", text_color=COLORS["success"])
        else:
            self.status_label.configure(text="  API key not set", text_color=COLORS["warning"])

    def _refresh_stats(self):
        nf = len(self.uploaded_files)
        nd = len(self.db_connections)
        ni = sum(1 for v in self.indexing_status.values() if v == "ready")
        self.stat_files.configure(text=str(nf))
        self.stat_dbs.configure(text=str(nd))
        self.stat_indexed.configure(text=str(ni))

    # ─────────────────────────────────────────────────────────────────────────
    #  MAIN PANEL (TABS)
    # ─────────────────────────────────────────────────────────────────────────
    def _build_main(self):
        main = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        self.tabview = ctk.CTkTabview(
            main, fg_color=COLORS["bg_dark"],
            segmented_button_fg_color=COLORS["bg_panel"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["bg_panel"],
            segmented_button_unselected_hover_color=COLORS["bg_card"],
        )
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        tab_chat = self.tabview.add("Chat")
        tab_files = self.tabview.add("Files")
        tab_databases = self.tabview.add("Databases")
        tab_sources = self.tabview.add("Sources")

        self._build_chat_tab(tab_chat)
        self._build_files_tab(tab_files)
        self._build_databases_tab(tab_databases)
        self._build_sources_tab(tab_sources)

    # ── CHAT TAB ─────────────────────────────────────────────────────────────
    def _build_chat_tab(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        ctk.CTkLabel(header, text="Ask your knowledge base",
                      font=ctk.CTkFont(size=20, weight="bold"),
                      text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Questions are answered using both uploaded files and connected databases.",
                      font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]).pack(anchor="w", pady=(2, 0))

        # Chat area (scrollable)
        self.chat_scroll = ctk.CTkScrollableFrame(
            parent, fg_color=COLORS["bg_panel"], corner_radius=12,
        )
        self.chat_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        self.chat_placeholder = ctk.CTkLabel(
            self.chat_scroll,
            text="\n\nYour knowledge base is ready\n\nUpload files or connect databases, then ask questions here.",
            font=ctk.CTkFont(size=14), text_color=COLORS["text_muted"], wraplength=400,
        )
        self.chat_placeholder.grid(row=0, column=0, pady=80)

        # Input row
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 4))
        input_frame.grid_columnconfigure(0, weight=1)

        self.chat_entry = ctk.CTkEntry(
            input_frame, placeholder_text="Ask a question about your knowledge base...",
            height=42, font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            text_color=COLORS["text_primary"],
        )
        self.chat_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.chat_entry.bind("<Return>", lambda e: self._send_message())

        ctk.CTkButton(
            input_frame, text="Send", width=80, height=42,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=self._send_message,
        ).grid(row=0, column=1)

        # Suggestion chips
        chip_frame = ctk.CTkFrame(parent, fg_color="transparent")
        chip_frame.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))

        suggestions = [
            "Summarize all documents",
            "What tables exist in my DB?",
            "Compare files & DB sources",
            "List key entities in my data",
        ]
        for i, s in enumerate(suggestions):
            ctk.CTkButton(
                chip_frame, text=s, height=30, font=ctk.CTkFont(size=11),
                fg_color=COLORS["bg_card"], hover_color=COLORS["bg_input"],
                text_color=COLORS["text_secondary"], corner_radius=16,
                command=lambda q=s: self._send_suggestion(q),
            ).pack(side="left", padx=(0, 6))

    def _send_suggestion(self, text):
        self.chat_entry.delete(0, "end")
        self.chat_entry.insert(0, text)
        self._send_message()

    def _send_message(self):
        query = self.chat_entry.get().strip()
        if not query:
            return

        self.chat_entry.delete(0, "end")

        # Hide placeholder
        self.chat_placeholder.grid_forget()

        # Add user message
        self.chat_history.append({"role": "user", "content": query})
        self._add_chat_bubble(query, is_user=True)

        # Placeholder response (wire your RAG pipeline here)
        provider = self.provider_var.get()
        model = self.model_var.get()
        nf = len(self.uploaded_files)
        nd = len(self.db_connections)
        response = (
            f"[Placeholder response]\n\n"
            f"Your question \"{query}\" would be answered by:\n"
            f"1. Embedding the query with {self.embed_var.get()}\n"
            f"2. Retrieving top-{self.topk_entry.get()} chunks from {nf} file(s) "
            f"and querying {nd} database(s)\n"
            f"3. Generating with {provider} / {model}\n\n"
            f"Connect your RAG backend to replace this stub."
        )
        sources = [f["name"] for f in self.uploaded_files[:2]]
        sources += [c["name"] for c in self.db_connections[:1]]
        if not sources:
            sources = ["No sources loaded yet"]

        self.chat_history.append({"role": "assistant", "content": response, "sources": sources})
        self._add_chat_bubble(response, is_user=False, sources=sources)

    def _add_chat_bubble(self, text, is_user=True, sources=None):
        row = len(self.chat_history) - 1

        outer = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        outer.grid(row=row, column=0, sticky="e" if is_user else "w", padx=8, pady=4)

        bubble = ctk.CTkFrame(
            outer, fg_color=COLORS["user_bubble"] if is_user else COLORS["assistant_bubble"],
            corner_radius=16,
        )
        bubble.pack(anchor="e" if is_user else "w")

        ctk.CTkLabel(
            bubble, text=text, wraplength=520, justify="left",
            font=ctk.CTkFont(size=13),
            text_color="#ffffff" if is_user else COLORS["text_primary"],
        ).pack(padx=14, pady=10)

        if sources and not is_user:
            src_text = "Sources: " + " | ".join(sources)
            ctk.CTkLabel(
                bubble, text=src_text, font=ctk.CTkFont(size=10),
                text_color=COLORS["text_muted"], wraplength=520, justify="left",
            ).pack(padx=14, pady=(0, 8))

        # Auto-scroll to bottom
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    # ── FILES TAB ────────────────────────────────────────────────────────────
    def _build_files_tab(self, parent):
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        ctk.CTkLabel(header, text="Upload Documents",
                      font=ctk.CTkFont(size=20, weight="bold"),
                      text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Supported: PDF, TXT, Markdown, HTML, CSV, JSON, XML, DOCX, RST, LOG",
                      font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]).pack(anchor="w", pady=(2, 0))

        # Buttons row
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=8)

        ctk.CTkButton(
            btn_frame, text="+ Add Files", height=38, fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], command=self._add_files,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text="Index All Pending", height=38,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], command=self._index_all,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text="Remove All", height=38,
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["error"], border_width=1, border_color=COLORS["error"],
            command=self._remove_all_files,
        ).pack(side="left")

        # File list (scrollable)
        self.files_scroll = ctk.CTkScrollableFrame(
            parent, fg_color=COLORS["bg_panel"], corner_radius=12,
        )
        self.files_scroll.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.files_scroll.grid_columnconfigure(1, weight=1)

        self.files_empty_label = ctk.CTkLabel(
            self.files_scroll,
            text="No files uploaded yet. Click \"+ Add Files\" to get started.",
            font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
        )
        self.files_empty_label.grid(row=0, column=0, columnspan=4, pady=60)

    def _add_files(self):
        paths = filedialog.askopenfilenames(
            title="Select files to upload",
            filetypes=SUPPORTED_EXTENSIONS,
        )
        if not paths:
            return

        for path in paths:
            name = os.path.basename(path)
            size = os.path.getsize(path)
            fid = file_id(name, size)

            if any(f["id"] == fid for f in self.uploaded_files):
                continue

            ext = name.rsplit(".", 1)[-1].lower() if "." in name else "txt"
            self.uploaded_files.append({
                "id": fid, "name": name, "size": size, "type": ext,
                "path": path, "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            self.indexing_status[fid] = "pending"

        self._refresh_file_list()
        self._refresh_stats()
        self._refresh_sources_list()

    def _index_all(self):
        for f in self.uploaded_files:
            if self.indexing_status.get(f["id"]) == "pending":
                # placeholder: actually run your indexing pipeline here
                self.indexing_status[f["id"]] = "ready"
        self._refresh_file_list()
        self._refresh_stats()
        self._refresh_sources_list()

    def _remove_all_files(self):
        if not self.uploaded_files:
            return
        if messagebox.askyesno("Confirm", "Remove all files from the knowledge base?"):
            file_ids = [f["id"] for f in self.uploaded_files]
            self.uploaded_files.clear()
            for fid in file_ids:
                self.indexing_status.pop(fid, None)
            self._refresh_file_list()
            self._refresh_stats()
            self._refresh_sources_list()

    def _remove_file(self, fid):
        self.uploaded_files = [f for f in self.uploaded_files if f["id"] != fid]
        self.indexing_status.pop(fid, None)
        self._refresh_file_list()
        self._refresh_stats()
        self._refresh_sources_list()

    def _refresh_file_list(self):
        for widget in self.files_scroll.winfo_children():
            widget.destroy()

        if not self.uploaded_files:
            self.files_empty_label = ctk.CTkLabel(
                self.files_scroll,
                text="No files uploaded yet. Click \"+ Add Files\" to get started.",
                font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
            )
            self.files_empty_label.grid(row=0, column=0, columnspan=4, pady=60)
            return

        self.files_scroll.grid_columnconfigure(1, weight=1)

        for i, f in enumerate(self.uploaded_files):
            status = self.indexing_status.get(f["id"], "pending")
            status_color = {"ready": COLORS["success"], "pending": COLORS["warning"],
                            "error": COLORS["error"]}.get(status, COLORS["text_muted"])

            row_frame = ctk.CTkFrame(self.files_scroll, fg_color=COLORS["bg_card"], corner_radius=10)
            row_frame.grid(row=i, column=0, columnspan=4, sticky="ew", padx=4, pady=3)
            row_frame.grid_columnconfigure(1, weight=1)

            ext_label = f.get("type", "txt").upper()
            ctk.CTkLabel(
                row_frame, text=ext_label, width=50,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS["accent"], fg_color=COLORS["bg_input"],
                corner_radius=6,
            ).grid(row=0, column=0, padx=(10, 8), pady=10)

            info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            info_frame.grid(row=0, column=1, sticky="ew", pady=6)

            ctk.CTkLabel(
                info_frame, text=f["name"], font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text_primary"], anchor="w",
            ).pack(anchor="w")
            ctk.CTkLabel(
                info_frame, text=f'{format_size(f["size"])}  |  {f["uploaded_at"]}',
                font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"], anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                row_frame, text=status.upper(), font=ctk.CTkFont(size=10, weight="bold"),
                text_color=status_color,
            ).grid(row=0, column=2, padx=8)

            ctk.CTkButton(
                row_frame, text="X", width=30, height=30, corner_radius=6,
                fg_color="transparent", hover_color=COLORS["bg_input"],
                text_color=COLORS["error"], font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda fid=f["id"]: self._remove_file(fid),
            ).grid(row=0, column=3, padx=(0, 8))

    # ── DATABASES TAB ────────────────────────────────────────────────────────
    def _build_databases_tab(self, parent):
        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        ctk.CTkLabel(header, text="Connect Databases",
                      font=ctk.CTkFont(size=20, weight="bold"),
                      text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Add SQL databases so the RAG system can query structured data.",
                      font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]).pack(anchor="w", pady=(2, 0))

        # Main scroll area for form + list
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        scroll.grid_columnconfigure(0, weight=1)

        # ── New Connection Form ──
        form = ctk.CTkFrame(scroll, fg_color=COLORS["bg_panel"], corner_radius=12)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        form.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(form, text="New Connection", font=ctk.CTkFont(size=14, weight="bold"),
                      text_color=COLORS["text_primary"]).grid(row=0, column=0, columnspan=2,
                                                               sticky="w", padx=16, pady=(12, 8))

        # Row 1: Name + Type
        ctk.CTkLabel(form, text="Connection Name", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).grid(row=1, column=0, sticky="w", padx=16)
        self.db_name_entry = ctk.CTkEntry(form, placeholder_text="e.g. Production DB",
                                           fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self.db_name_entry.grid(row=2, column=0, sticky="ew", padx=16, pady=(2, 8))

        ctk.CTkLabel(form, text="Database Type", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).grid(row=1, column=1, sticky="w", padx=16)
        self.db_type_var = ctk.StringVar(value="PostgreSQL")
        self.db_type_menu = ctk.CTkOptionMenu(
            form, variable=self.db_type_var, values=["SQLite", "PostgreSQL", "MySQL"],
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"], command=self._on_db_type_change,
        )
        self.db_type_menu.grid(row=2, column=1, sticky="ew", padx=16, pady=(2, 8))

        # Row 2: Host + Port (or file path for SQLite)
        ctk.CTkLabel(form, text="Host", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).grid(row=3, column=0, sticky="w", padx=16)
        self.db_host_entry = ctk.CTkEntry(form, placeholder_text="localhost",
                                           fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self.db_host_entry.grid(row=4, column=0, sticky="ew", padx=16, pady=(2, 8))

        ctk.CTkLabel(form, text="Port", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).grid(row=3, column=1, sticky="w", padx=16)
        self.db_port_entry = ctk.CTkEntry(form, placeholder_text="5432",
                                           fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self.db_port_entry.grid(row=4, column=1, sticky="ew", padx=16, pady=(2, 8))

        # Row 3: Database + User
        ctk.CTkLabel(form, text="Database", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).grid(row=5, column=0, sticky="w", padx=16)
        self.db_database_entry = ctk.CTkEntry(form, placeholder_text="mydb",
                                               fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self.db_database_entry.grid(row=6, column=0, sticky="ew", padx=16, pady=(2, 8))

        ctk.CTkLabel(form, text="Username", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).grid(row=5, column=1, sticky="w", padx=16)
        self.db_user_entry = ctk.CTkEntry(form, placeholder_text="postgres",
                                           fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self.db_user_entry.grid(row=6, column=1, sticky="ew", padx=16, pady=(2, 8))

        # Row 4: Password + SSL
        ctk.CTkLabel(form, text="Password", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).grid(row=7, column=0, sticky="w", padx=16)
        self.db_pass_entry = ctk.CTkEntry(form, show="*", placeholder_text="password",
                                           fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self.db_pass_entry.grid(row=8, column=0, sticky="ew", padx=16, pady=(2, 8))

        ssl_frame = ctk.CTkFrame(form, fg_color="transparent")
        ssl_frame.grid(row=8, column=1, sticky="w", padx=16, pady=(2, 8))
        self.db_ssl_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(ssl_frame, text="Use SSL", variable=self.db_ssl_var,
                         text_color=COLORS["text_secondary"]).pack(anchor="w")

        # Scope
        ctk.CTkLabel(form, text="ACCESS SCOPE (OPTIONAL)", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=9, column=0, columnspan=2,
                                                             sticky="w", padx=16, pady=(8, 4))

        ctk.CTkLabel(form, text="Schemas (comma-separated)", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).grid(row=10, column=0, sticky="w", padx=16)
        self.db_schemas_entry = ctk.CTkEntry(form, placeholder_text="public, analytics",
                                              fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self.db_schemas_entry.grid(row=11, column=0, sticky="ew", padx=16, pady=(2, 8))

        ctk.CTkLabel(form, text="Tables (comma-separated)", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).grid(row=10, column=1, sticky="w", padx=16)
        self.db_tables_entry = ctk.CTkEntry(form, placeholder_text="users, orders",
                                             fg_color=COLORS["bg_input"], border_color=COLORS["border"])
        self.db_tables_entry.grid(row=11, column=1, sticky="ew", padx=16, pady=(2, 8))

        ctk.CTkLabel(form, text="Description (helps LLM write better queries)", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).grid(row=12, column=0, columnspan=2,
                                                                 sticky="w", padx=16)
        self.db_desc_entry = ctk.CTkTextbox(form, height=60, fg_color=COLORS["bg_input"],
                                             border_color=COLORS["border"], border_width=1,
                                             text_color=COLORS["text_primary"])
        self.db_desc_entry.grid(row=13, column=0, columnspan=2, sticky="ew", padx=16, pady=(2, 8))

        # Buttons
        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=14, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 16))

        ctk.CTkButton(
            btn_row, text="Add Connection", height=38,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=self._add_db_connection,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="Test Connection", height=38,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], command=self._test_db_connection,
        ).pack(side="left")

        # ── SQLite path browse (hidden for non-sqlite) ──
        self.db_browse_btn = ctk.CTkButton(
            form, text="Browse...", width=80, height=28, font=ctk.CTkFont(size=11),
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_input"],
            text_color=COLORS["text_secondary"], command=self._browse_sqlite,
        )
        # initially hidden

        # ── Existing connections list ──
        ctk.CTkLabel(scroll, text="ACTIVE CONNECTIONS", font=ctk.CTkFont(size=10, weight="bold"),
                      text_color=COLORS["text_muted"]).grid(row=1, column=0, sticky="w", padx=4, pady=(4, 4))

        self.db_list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.db_list_frame.grid(row=2, column=0, sticky="ew")
        self.db_list_frame.grid_columnconfigure(0, weight=1)

        self.db_empty_label = ctk.CTkLabel(
            self.db_list_frame,
            text="No databases connected. Use the form above to add one.",
            font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
        )
        self.db_empty_label.grid(row=0, column=0, pady=30)

    def _on_db_type_change(self, choice):
        if choice == "SQLite":
            self.db_host_entry.configure(placeholder_text="/path/to/database.db", state="normal")
            self.db_port_entry.configure(state="disabled")
            self.db_database_entry.configure(state="disabled")
            self.db_user_entry.configure(state="disabled")
            self.db_pass_entry.configure(state="disabled")
        else:
            port = "5432" if choice == "PostgreSQL" else "3306"
            self.db_host_entry.configure(placeholder_text="localhost", state="normal")
            self.db_port_entry.configure(state="normal", placeholder_text=port)
            self.db_database_entry.configure(state="normal")
            self.db_user_entry.configure(state="normal")
            self.db_pass_entry.configure(state="normal")

    def _browse_sqlite(self):
        path = filedialog.askopenfilename(filetypes=[("SQLite", "*.db *.sqlite *.sqlite3"), ("All", "*.*")])
        if path:
            self.db_host_entry.delete(0, "end")
            self.db_host_entry.insert(0, path)

    def _test_db_connection(self):
        messagebox.showinfo("Test Connection",
                            "Connection test placeholder -- wire up your DB driver here.")

    def _add_db_connection(self):
        name = self.db_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a connection name.")
            return

        db_type = self.db_type_var.get()
        cid = hashlib.md5(f"{name}{datetime.now()}".encode()).hexdigest()[:10]

        conn = {
            "id": cid, "name": name, "type": db_type,
            "connected_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "description": self.db_desc_entry.get("1.0", "end").strip(),
            "schemas": [s.strip() for s in self.db_schemas_entry.get().split(",") if s.strip()],
            "tables": [t.strip() for t in self.db_tables_entry.get().split(",") if t.strip()],
        }

        if db_type == "SQLite":
            conn["path"] = self.db_host_entry.get().strip()
        else:
            conn["host"] = self.db_host_entry.get().strip()
            conn["port"] = self.db_port_entry.get().strip()
            conn["database"] = self.db_database_entry.get().strip()
            conn["user"] = self.db_user_entry.get().strip()

        self.db_connections.append(conn)
        self.indexing_status[cid] = "ready"

        # Clear form
        self.db_name_entry.delete(0, "end")
        self.db_host_entry.delete(0, "end")
        self.db_port_entry.delete(0, "end")
        self.db_database_entry.delete(0, "end")
        self.db_user_entry.delete(0, "end")
        self.db_pass_entry.delete(0, "end")
        self.db_schemas_entry.delete(0, "end")
        self.db_tables_entry.delete(0, "end")
        self.db_desc_entry.delete("1.0", "end")

        self._refresh_db_list()
        self._refresh_stats()
        self._refresh_sources_list()

    def _remove_db(self, cid):
        self.db_connections = [c for c in self.db_connections if c["id"] != cid]
        self.indexing_status.pop(cid, None)
        self._refresh_db_list()
        self._refresh_stats()
        self._refresh_sources_list()

    def _refresh_db_list(self):
        for w in self.db_list_frame.winfo_children():
            w.destroy()

        if not self.db_connections:
            ctk.CTkLabel(
                self.db_list_frame,
                text="No databases connected. Use the form above to add one.",
                font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
            ).grid(row=0, column=0, pady=30)
            return

        self.db_list_frame.grid_columnconfigure(0, weight=1)

        for i, conn in enumerate(self.db_connections):
            card = ctk.CTkFrame(self.db_list_frame, fg_color=COLORS["bg_card"], corner_radius=10)
            card.grid(row=i, column=0, sticky="ew", pady=3)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                card, text=conn["type"][:4].upper(), width=50,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS["success"], fg_color=COLORS["bg_input"], corner_radius=6,
            ).grid(row=0, column=0, padx=(10, 8), pady=10)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.grid(row=0, column=1, sticky="ew", pady=6)

            location = conn.get("path") or f'{conn.get("host", "")}:{conn.get("port", "")}/{conn.get("database", "")}'
            ctk.CTkLabel(info, text=conn["name"], font=ctk.CTkFont(size=13, weight="bold"),
                          text_color=COLORS["text_primary"]).pack(anchor="w")
            ctk.CTkLabel(info, text=f'{conn["type"]}  |  {location}',
                          font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"]).pack(anchor="w")
            if conn.get("description"):
                ctk.CTkLabel(info, text=conn["description"], font=ctk.CTkFont(size=10),
                              text_color=COLORS["text_muted"], wraplength=400).pack(anchor="w")

            ctk.CTkLabel(card, text="CONNECTED", font=ctk.CTkFont(size=10, weight="bold"),
                          text_color=COLORS["success"]).grid(row=0, column=2, padx=8)

            ctk.CTkButton(
                card, text="X", width=30, height=30, corner_radius=6,
                fg_color="transparent", hover_color=COLORS["bg_input"],
                text_color=COLORS["error"], font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda cid=conn["id"]: self._remove_db(cid),
            ).grid(row=0, column=3, padx=(0, 8))

    # ── SOURCES TAB ──────────────────────────────────────────────────────────
    def _build_sources_tab(self, parent):
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        ctk.CTkLabel(header, text="Knowledge Base Sources",
                      font=ctk.CTkFont(size=20, weight="bold"),
                      text_color=COLORS["text_primary"]).pack(anchor="w")
        ctk.CTkLabel(header, text="Overview of all data sources powering the RAG system.",
                      font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"]).pack(anchor="w", pady=(2, 0))

        # Filters
        filter_frame = ctk.CTkFrame(parent, fg_color="transparent")
        filter_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=8)

        ctk.CTkLabel(filter_frame, text="Type:", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 4))
        self.src_kind_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(
            filter_frame, variable=self.src_kind_var, values=["All", "Files", "Databases"],
            width=120, fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"], command=lambda _: self._refresh_sources_list(),
        ).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(filter_frame, text="Status:", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 4))
        self.src_status_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(
            filter_frame, variable=self.src_status_var, values=["All", "Ready", "Pending"],
            width=120, fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"], command=lambda _: self._refresh_sources_list(),
        ).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(filter_frame, text="Search:", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 4))
        self.src_search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            filter_frame, textvariable=self.src_search_var, width=200,
            placeholder_text="Filter by name...",
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
        )
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda _: self._refresh_sources_list())

        # Sources list
        self.sources_scroll = ctk.CTkScrollableFrame(
            parent, fg_color=COLORS["bg_panel"], corner_radius=12,
        )
        self.sources_scroll.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.sources_scroll.grid_columnconfigure(1, weight=1)

        self.sources_empty = ctk.CTkLabel(
            self.sources_scroll,
            text="No sources yet. Upload files or connect databases to populate your knowledge base.",
            font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
        )
        self.sources_empty.grid(row=0, column=0, columnspan=3, pady=60)

    def _refresh_sources_list(self):
        for w in self.sources_scroll.winfo_children():
            w.destroy()

        all_sources = []
        for f in self.uploaded_files:
            status = self.indexing_status.get(f["id"], "pending")
            all_sources.append({
                "kind": "file", "name": f["name"],
                "detail": f'{format_size(f["size"])}  |  {f["uploaded_at"]}',
                "status": status,
            })
        for c in self.db_connections:
            loc = c.get("path") or f'{c.get("host", "")}:{c.get("port", "")}/{c.get("database", "")}'
            all_sources.append({
                "kind": "db", "name": c["name"],
                "detail": f'{c["type"]}  |  {loc}',
                "status": "ready",
            })

        # Apply filters
        kind = self.src_kind_var.get()
        if kind == "Files":
            all_sources = [s for s in all_sources if s["kind"] == "file"]
        elif kind == "Databases":
            all_sources = [s for s in all_sources if s["kind"] == "db"]

        status_filter = self.src_status_var.get()
        if status_filter != "All":
            all_sources = [s for s in all_sources if s["status"] == status_filter.lower()]

        search = self.src_search_var.get().strip().lower()
        if search:
            all_sources = [s for s in all_sources if search in s["name"].lower()]

        if not all_sources:
            ctk.CTkLabel(
                self.sources_scroll,
                text="No sources match the current filters.",
                font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
            ).grid(row=0, column=0, columnspan=3, pady=60)
            return

        self.sources_scroll.grid_columnconfigure(1, weight=1)

        for i, src in enumerate(all_sources):
            status_color = {"ready": COLORS["success"], "pending": COLORS["warning"],
                            "error": COLORS["error"]}.get(src["status"], COLORS["text_muted"])
            kind_color = COLORS["accent"] if src["kind"] == "file" else COLORS["success"]
            kind_text = "FILE" if src["kind"] == "file" else "DB"

            row = ctk.CTkFrame(self.sources_scroll, fg_color=COLORS["bg_card"], corner_radius=10)
            row.grid(row=i, column=0, columnspan=3, sticky="ew", padx=4, pady=3)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row, text=kind_text, width=44,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=kind_color, fg_color=COLORS["bg_input"], corner_radius=6,
            ).grid(row=0, column=0, padx=(10, 8), pady=10)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.grid(row=0, column=1, sticky="ew", pady=6)
            ctk.CTkLabel(info, text=src["name"], font=ctk.CTkFont(size=13, weight="bold"),
                          text_color=COLORS["text_primary"]).pack(anchor="w")
            ctk.CTkLabel(info, text=src["detail"], font=ctk.CTkFont(size=11),
                          text_color=COLORS["text_muted"]).pack(anchor="w")

            ctk.CTkLabel(
                row, text=src["status"].upper(),
                font=ctk.CTkFont(size=10, weight="bold"), text_color=status_color,
            ).grid(row=0, column=2, padx=12)


# ═════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = RAGApp()
    app.mainloop()
