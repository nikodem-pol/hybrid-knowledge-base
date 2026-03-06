"""
Files tab: upload documents, view per-file indexing status, bulk actions.
"""

import os
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .config import COLORS, SUPPORTED_EXTENSIONS
from .helpers import file_id, format_size


class FilesTab:
    """Builds and manages the Files tab."""

    def __init__(self, parent: ctk.CTkFrame, app):
        self.app = app

        parent.grid_rowconfigure(2, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        ctk.CTkLabel(
            header, text="Upload Documents",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Supported: PDF, TXT, Markdown, HTML, CSV, JSON, XML, DOCX, RST, LOG",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        # Action buttons
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=8, pady=8)

        ctk.CTkButton(
            btn_frame, text="+ Add Files", height=38,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=self._add_files,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text="Index All Pending", height=38,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            command=self._index_all,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame, text="Remove All", height=38,
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["error"], border_width=1, border_color=COLORS["error"],
            command=self._remove_all,
        ).pack(side="left")

        # File list
        self.scroll = ctk.CTkScrollableFrame(
            parent, fg_color=COLORS["bg_panel"], corner_radius=12,
        )
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.scroll.grid_columnconfigure(1, weight=1)

        self._empty_label = ctk.CTkLabel(
            self.scroll,
            text='No files uploaded yet. Click "+ Add Files" to get started.',
            font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
        )
        self._empty_label.grid(row=0, column=0, columnspan=4, pady=60)

    # ── actions ──────────────────────────────────────────────────────────────
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

            if any(f["id"] == fid for f in self.app.uploaded_files):
                continue

            ext = name.rsplit(".", 1)[-1].lower() if "." in name else "txt"
            self.app.uploaded_files.append({
                "id": fid, "name": name, "size": size, "type": ext,
                "path": path, "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            })
            self.app.indexing_status[fid] = "pending"

        self._refresh()
        self.app.notify_sources_changed()

    def _index_all(self):
        for f in self.app.uploaded_files:
            if self.app.indexing_status.get(f["id"]) == "pending":
                # placeholder: run your indexing pipeline here
                self.app.indexing_status[f["id"]] = "ready"
        self._refresh()
        self.app.notify_sources_changed()

    def _remove_all(self):
        if not self.app.uploaded_files:
            return
        if messagebox.askyesno("Confirm", "Remove all files from the knowledge base?"):
            for f in self.app.uploaded_files:
                self.app.indexing_status.pop(f["id"], None)
            self.app.uploaded_files.clear()
            self._refresh()
            self.app.notify_sources_changed()

    def _remove_one(self, fid: str):
        self.app.uploaded_files = [f for f in self.app.uploaded_files if f["id"] != fid]
        self.app.indexing_status.pop(fid, None)
        self._refresh()
        self.app.notify_sources_changed()

    # ── rendering ────────────────────────────────────────────────────────────
    def _refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        if not self.app.uploaded_files:
            self._empty_label = ctk.CTkLabel(
                self.scroll,
                text='No files uploaded yet. Click "+ Add Files" to get started.',
                font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
            )
            self._empty_label.grid(row=0, column=0, columnspan=4, pady=60)
            return

        self.scroll.grid_columnconfigure(1, weight=1)

        for i, f in enumerate(self.app.uploaded_files):
            status = self.app.indexing_status.get(f["id"], "pending")
            status_color = {
                "ready": COLORS["success"],
                "pending": COLORS["warning"],
                "error": COLORS["error"],
            }.get(status, COLORS["text_muted"])

            row = ctk.CTkFrame(self.scroll, fg_color=COLORS["bg_card"], corner_radius=10)
            row.grid(row=i, column=0, columnspan=4, sticky="ew", padx=4, pady=3)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row, text=f.get("type", "txt").upper(), width=50,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS["accent"], fg_color=COLORS["bg_input"], corner_radius=6,
            ).grid(row=0, column=0, padx=(10, 8), pady=10)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.grid(row=0, column=1, sticky="ew", pady=6)
            ctk.CTkLabel(
                info, text=f["name"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text_primary"], anchor="w",
            ).pack(anchor="w")
            ctk.CTkLabel(
                info,
                text=f'{format_size(f["size"])}  |  {f["uploaded_at"]}',
                font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"], anchor="w",
            ).pack(anchor="w")

            ctk.CTkLabel(
                row, text=status.upper(),
                font=ctk.CTkFont(size=10, weight="bold"), text_color=status_color,
            ).grid(row=0, column=2, padx=8)

            ctk.CTkButton(
                row, text="X", width=30, height=30, corner_radius=6,
                fg_color="transparent", hover_color=COLORS["bg_input"],
                text_color=COLORS["error"],
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda fid=f["id"]: self._remove_one(fid),
            ).grid(row=0, column=3, padx=(0, 8))
