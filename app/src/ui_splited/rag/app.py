"""
Main application window: wires sidebar + tabs together, holds shared state.
"""

import customtkinter as ctk

from .config import COLORS
from .sidebar import Sidebar
from .tab_chat import ChatTab
from .tab_files import FilesTab
from .tab_databases import DatabasesTab
from .tab_sources import SourcesTab

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class RAGApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RAG Knowledge Base")
        self.geometry("1280x820")
        self.minsize(960, 640)
        self.configure(fg_color=COLORS["bg_dark"])

        # ── Shared state ──
        self.uploaded_files: list[dict] = []
        self.db_connections: list[dict] = []
        self.indexing_status: dict[str, str] = {}

        # ── Layout ──
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = Sidebar(self)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Main panel with tabs
        main = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"], corner_radius=0)
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)

        tabview = ctk.CTkTabview(
            main, fg_color=COLORS["bg_dark"],
            segmented_button_fg_color=COLORS["bg_panel"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["bg_panel"],
            segmented_button_unselected_hover_color=COLORS["bg_card"],
        )
        tabview.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        # Build each tab
        self.tab_chat = ChatTab(tabview.add("Chat"), self)
        self.tab_files = FilesTab(tabview.add("Files"), self)
        self.tab_databases = DatabasesTab(tabview.add("Databases"), self)
        self.tab_sources = SourcesTab(tabview.add("Sources"), self)

    def notify_sources_changed(self):
        """Called by tabs after files/dbs change to keep stats + sources in sync."""
        nf = len(self.uploaded_files)
        nd = len(self.db_connections)
        ni = sum(1 for v in self.indexing_status.values() if v == "ready")
        self.sidebar.refresh_stats(nf, nd, ni)
        self.tab_sources.refresh()
