"""
Sources tab: unified filterable list of all knowledge-base sources (files + DBs).
"""

import customtkinter as ctk

from .config import COLORS
from .helpers import format_size


class SourcesTab:
    """Builds and manages the Sources overview tab."""

    def __init__(self, parent: ctk.CTkFrame, app):
        self.app = app

        parent.grid_rowconfigure(2, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        ctk.CTkLabel(
            header, text="Knowledge Base Sources",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Overview of all data sources powering the RAG system.",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        # Filters
        filt = ctk.CTkFrame(parent, fg_color="transparent")
        filt.grid(row=1, column=0, sticky="ew", padx=8, pady=8)

        ctk.CTkLabel(filt, text="Type:", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 4))
        self.kind_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(
            filt, variable=self.kind_var,
            values=["All", "Files", "Databases"], width=120,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            command=lambda _: self.refresh(),
        ).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(filt, text="Status:", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 4))
        self.status_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(
            filt, variable=self.status_var,
            values=["All", "Ready", "Pending"], width=120,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            command=lambda _: self.refresh(),
        ).pack(side="left", padx=(0, 16))

        ctk.CTkLabel(filt, text="Search:", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(side="left", padx=(0, 4))
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            filt, textvariable=self.search_var, width=200,
            placeholder_text="Filter by name...",
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
        )
        search_entry.pack(side="left")
        search_entry.bind("<KeyRelease>", lambda _: self.refresh())

        # List
        self.scroll = ctk.CTkScrollableFrame(
            parent, fg_color=COLORS["bg_panel"], corner_radius=12,
        )
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.scroll.grid_columnconfigure(1, weight=1)

        self._show_empty("No sources yet. Upload files or connect databases to populate your knowledge base.")

    # ── public ───────────────────────────────────────────────────────────────
    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        sources = self._gather_sources()
        sources = self._apply_filters(sources)

        if not sources:
            self._show_empty("No sources match the current filters.")
            return

        self.scroll.grid_columnconfigure(1, weight=1)

        for i, src in enumerate(sources):
            status_color = {
                "ready": COLORS["success"],
                "pending": COLORS["warning"],
                "error": COLORS["error"],
            }.get(src["status"], COLORS["text_muted"])
            kind_color = COLORS["accent"] if src["kind"] == "file" else COLORS["success"]
            kind_text = "FILE" if src["kind"] == "file" else "DB"

            row = ctk.CTkFrame(self.scroll, fg_color=COLORS["bg_card"], corner_radius=10)
            row.grid(row=i, column=0, columnspan=3, sticky="ew", padx=4, pady=3)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row, text=kind_text, width=44,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=kind_color, fg_color=COLORS["bg_input"], corner_radius=6,
            ).grid(row=0, column=0, padx=(10, 8), pady=10)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.grid(row=0, column=1, sticky="ew", pady=6)
            ctk.CTkLabel(
                info, text=src["name"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text_primary"],
            ).pack(anchor="w")
            ctk.CTkLabel(
                info, text=src["detail"],
                font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"],
            ).pack(anchor="w")

            ctk.CTkLabel(
                row, text=src["status"].upper(),
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=status_color,
            ).grid(row=0, column=2, padx=12)

    # ── private ──────────────────────────────────────────────────────────────
    def _gather_sources(self) -> list[dict]:
        sources = []
        for f in self.app.uploaded_files:
            status = self.app.indexing_status.get(f["id"], "pending")
            sources.append({
                "kind": "file", "name": f["name"],
                "detail": f'{format_size(f["size"])}  |  {f["uploaded_at"]}',
                "status": status,
            })
        for c in self.app.db_connections:
            loc = c.get("path") or (
                f'{c.get("host", "")}:{c.get("port", "")}/{c.get("database", "")}'
            )
            sources.append({
                "kind": "db", "name": c["name"],
                "detail": f'{c["type"]}  |  {loc}',
                "status": "ready",
            })
        return sources

    def _apply_filters(self, sources: list[dict]) -> list[dict]:
        kind = self.kind_var.get()
        if kind == "Files":
            sources = [s for s in sources if s["kind"] == "file"]
        elif kind == "Databases":
            sources = [s for s in sources if s["kind"] == "db"]

        status = self.status_var.get()
        if status != "All":
            sources = [s for s in sources if s["status"] == status.lower()]

        search = self.search_var.get().strip().lower()
        if search:
            sources = [s for s in sources if search in s["name"].lower()]

        return sources

    def _show_empty(self, text: str):
        ctk.CTkLabel(
            self.scroll, text=text,
            font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
        ).grid(row=0, column=0, columnspan=3, pady=60)
