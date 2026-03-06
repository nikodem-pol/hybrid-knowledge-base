"""
Databases tab: connection form, type-aware fields, active connection list.
"""

import hashlib
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .config import COLORS


class DatabasesTab:
    """Builds and manages the Databases tab."""

    def __init__(self, parent: ctk.CTkFrame, app):
        self.app = app

        parent.grid_rowconfigure(1, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        ctk.CTkLabel(
            header, text="Connect Databases",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Add SQL databases so the RAG system can query structured data.",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"],
        ).pack(anchor="w", pady=(2, 0))

        # Scroll wrapper
        scroll = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        scroll.grid_columnconfigure(0, weight=1)

        # ── Form ──
        form = ctk.CTkFrame(scroll, fg_color=COLORS["bg_panel"], corner_radius=12)
        form.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        form.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            form, text="New Connection",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"],
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=16, pady=(12, 8))

        # Row 1 — Name + Type
        self._form_label(form, "Connection Name", 1, 0)
        self.name_entry = self._form_entry(form, "e.g. Production DB", 2, 0)

        self._form_label(form, "Database Type", 1, 1)
        self.type_var = ctk.StringVar(value="PostgreSQL")
        self.type_menu = ctk.CTkOptionMenu(
            form, variable=self.type_var,
            values=["SQLite", "PostgreSQL", "MySQL"],
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
            command=self._on_type_change,
        )
        self.type_menu.grid(row=2, column=1, sticky="ew", padx=16, pady=(2, 8))

        # Row 2 — Host + Port
        self._form_label(form, "Host", 3, 0)
        self.host_entry = self._form_entry(form, "localhost", 4, 0)

        self._form_label(form, "Port", 3, 1)
        self.port_entry = self._form_entry(form, "5432", 4, 1)

        # Row 3 — Database + Username
        self._form_label(form, "Database", 5, 0)
        self.database_entry = self._form_entry(form, "mydb", 6, 0)

        self._form_label(form, "Username", 5, 1)
        self.user_entry = self._form_entry(form, "postgres", 6, 1)

        # Row 4 — Password + SSL
        self._form_label(form, "Password", 7, 0)
        self.pass_entry = self._form_entry(form, "password", 8, 0, show="*")

        ssl_frame = ctk.CTkFrame(form, fg_color="transparent")
        ssl_frame.grid(row=8, column=1, sticky="w", padx=16, pady=(2, 8))
        self.ssl_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            ssl_frame, text="Use SSL", variable=self.ssl_var,
            text_color=COLORS["text_secondary"],
        ).pack(anchor="w")

        # Scope
        ctk.CTkLabel(
            form, text="ACCESS SCOPE (OPTIONAL)",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_muted"],
        ).grid(row=9, column=0, columnspan=2, sticky="w", padx=16, pady=(8, 4))

        self._form_label(form, "Schemas (comma-separated)", 10, 0)
        self.schemas_entry = self._form_entry(form, "public, analytics", 11, 0)

        self._form_label(form, "Tables (comma-separated)", 10, 1)
        self.tables_entry = self._form_entry(form, "users, orders", 11, 1)

        self._form_label(form, "Description (helps LLM write better queries)", 12, 0, colspan=2)
        self.desc_text = ctk.CTkTextbox(
            form, height=60, fg_color=COLORS["bg_input"],
            border_color=COLORS["border"], border_width=1,
            text_color=COLORS["text_primary"],
        )
        self.desc_text.grid(row=13, column=0, columnspan=2, sticky="ew", padx=16, pady=(2, 8))

        # Buttons
        btn_row = ctk.CTkFrame(form, fg_color="transparent")
        btn_row.grid(row=14, column=0, columnspan=2, sticky="ew", padx=16, pady=(0, 16))

        ctk.CTkButton(
            btn_row, text="Add Connection", height=38,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=self._add_connection,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_row, text="Test Connection", height=38,
            fg_color=COLORS["bg_card"], hover_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"],
            command=self._test_connection,
        ).pack(side="left")

        # ── Active connections list ──
        ctk.CTkLabel(
            scroll, text="ACTIVE CONNECTIONS",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=COLORS["text_muted"],
        ).grid(row=1, column=0, sticky="w", padx=4, pady=(4, 4))

        self.list_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.list_frame.grid(row=2, column=0, sticky="ew")
        self.list_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.list_frame,
            text="No databases connected. Use the form above to add one.",
            font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
        ).grid(row=0, column=0, pady=30)

    # ── form helpers ─────────────────────────────────────────────────────────
    @staticmethod
    def _form_label(parent, text, row, col, colspan=1):
        ctk.CTkLabel(
            parent, text=text, font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
        ).grid(row=row, column=col, columnspan=colspan, sticky="w", padx=16)

    @staticmethod
    def _form_entry(parent, placeholder, row, col, show=""):
        entry = ctk.CTkEntry(
            parent, placeholder_text=placeholder,
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
            show=show,
        )
        entry.grid(row=row, column=col, sticky="ew", padx=16, pady=(2, 8))
        return entry

    # ── actions ──────────────────────────────────────────────────────────────
    def _on_type_change(self, choice):
        if choice == "SQLite":
            self.host_entry.configure(placeholder_text="/path/to/database.db", state="normal")
            self.port_entry.configure(state="disabled")
            self.database_entry.configure(state="disabled")
            self.user_entry.configure(state="disabled")
            self.pass_entry.configure(state="disabled")
        else:
            port = "5432" if choice == "PostgreSQL" else "3306"
            self.host_entry.configure(placeholder_text="localhost", state="normal")
            self.port_entry.configure(state="normal", placeholder_text=port)
            self.database_entry.configure(state="normal")
            self.user_entry.configure(state="normal")
            self.pass_entry.configure(state="normal")

    def _test_connection(self):
        messagebox.showinfo(
            "Test Connection",
            "Connection test placeholder -- wire up your DB driver here.",
        )

    def _add_connection(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter a connection name.")
            return

        db_type = self.type_var.get()
        cid = hashlib.md5(f"{name}{datetime.now()}".encode()).hexdigest()[:10]

        conn: dict = {
            "id": cid, "name": name, "type": db_type,
            "connected_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "description": self.desc_text.get("1.0", "end").strip(),
            "schemas": [s.strip() for s in self.schemas_entry.get().split(",") if s.strip()],
            "tables": [t.strip() for t in self.tables_entry.get().split(",") if t.strip()],
        }

        if db_type == "SQLite":
            conn["path"] = self.host_entry.get().strip()
        else:
            conn["host"] = self.host_entry.get().strip()
            conn["port"] = self.port_entry.get().strip()
            conn["database"] = self.database_entry.get().strip()
            conn["user"] = self.user_entry.get().strip()

        self.app.db_connections.append(conn)
        self.app.indexing_status[cid] = "ready"

        # Clear form
        for entry in (
            self.name_entry, self.host_entry, self.port_entry,
            self.database_entry, self.user_entry, self.pass_entry,
            self.schemas_entry, self.tables_entry,
        ):
            entry.delete(0, "end")
        self.desc_text.delete("1.0", "end")

        self._refresh()
        self.app.notify_sources_changed()

    def _remove(self, cid: str):
        self.app.db_connections = [c for c in self.app.db_connections if c["id"] != cid]
        self.app.indexing_status.pop(cid, None)
        self._refresh()
        self.app.notify_sources_changed()

    # ── rendering ────────────────────────────────────────────────────────────
    def _refresh(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        if not self.app.db_connections:
            ctk.CTkLabel(
                self.list_frame,
                text="No databases connected. Use the form above to add one.",
                font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
            ).grid(row=0, column=0, pady=30)
            return

        self.list_frame.grid_columnconfigure(0, weight=1)

        for i, conn in enumerate(self.app.db_connections):
            card = ctk.CTkFrame(self.list_frame, fg_color=COLORS["bg_card"], corner_radius=10)
            card.grid(row=i, column=0, sticky="ew", pady=3)
            card.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                card, text=conn["type"][:4].upper(), width=50,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS["success"], fg_color=COLORS["bg_input"], corner_radius=6,
            ).grid(row=0, column=0, padx=(10, 8), pady=10)

            info = ctk.CTkFrame(card, fg_color="transparent")
            info.grid(row=0, column=1, sticky="ew", pady=6)

            location = conn.get("path") or (
                f'{conn.get("host", "")}:{conn.get("port", "")}/{conn.get("database", "")}'
            )
            ctk.CTkLabel(
                info, text=conn["name"],
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text_primary"],
            ).pack(anchor="w")
            ctk.CTkLabel(
                info, text=f'{conn["type"]}  |  {location}',
                font=ctk.CTkFont(size=11), text_color=COLORS["text_muted"],
            ).pack(anchor="w")

            if conn.get("description"):
                ctk.CTkLabel(
                    info, text=conn["description"],
                    font=ctk.CTkFont(size=10), text_color=COLORS["text_muted"],
                    wraplength=400,
                ).pack(anchor="w")

            ctk.CTkLabel(
                card, text="CONNECTED",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=COLORS["success"],
            ).grid(row=0, column=2, padx=8)

            ctk.CTkButton(
                card, text="X", width=30, height=30, corner_radius=6,
                fg_color="transparent", hover_color=COLORS["bg_input"],
                text_color=COLORS["error"],
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda cid=conn["id"]: self._remove(cid),
            ).grid(row=0, column=3, padx=(0, 8))
