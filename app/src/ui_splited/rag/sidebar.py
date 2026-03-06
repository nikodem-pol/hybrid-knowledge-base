"""
Left sidebar: LLM provider/model/key, advanced settings, KB stats, status.
"""

import customtkinter as ctk
from .config import COLORS, LLM_MODELS, EMBEDDING_MODELS


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, width=300, corner_radius=0, fg_color=COLORS["bg_panel"], **kwargs)
        self.grid_propagate(False)

        pad = {"padx": 16, "pady": (0, 0)}

        # ── Title ──
        ctk.CTkLabel(
            self, text="RAG Knowledge Base",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["text_primary"],
        ).pack(padx=16, pady=(20, 2), anchor="w")

        ctk.CTkLabel(
            self, text="Hybrid retrieval from files & databases",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_muted"],
        ).pack(padx=16, pady=(0, 12), anchor="w")

        self._sep()

        # ── LLM CONFIG ──
        self._section("LLM CONFIGURATION")

        ctk.CTkLabel(self, text="Provider", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(**pad, anchor="w")
        self.provider_var = ctk.StringVar(value="OpenAI")
        self.provider_menu = ctk.CTkOptionMenu(
            self, variable=self.provider_var, values=list(LLM_MODELS.keys()),
            command=self._on_provider_change,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
        )
        self.provider_menu.pack(padx=16, pady=(2, 8), fill="x")

        ctk.CTkLabel(self, text="Model", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(**pad, anchor="w")
        self.model_var = ctk.StringVar(value="gpt-4o")
        self.model_menu = ctk.CTkOptionMenu(
            self, variable=self.model_var, values=LLM_MODELS["OpenAI"],
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
        )
        self.model_menu.pack(padx=16, pady=(2, 8), fill="x")

        ctk.CTkLabel(self, text="API Key", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(**pad, anchor="w")
        self.api_key_entry = ctk.CTkEntry(
            self, placeholder_text="sk-...", show="*",
            fg_color=COLORS["bg_input"], border_color=COLORS["border"],
        )
        self.api_key_entry.pack(padx=16, pady=(2, 8), fill="x")

        # ── Advanced toggle ──
        self._adv_visible = False
        self._adv_toggle = ctk.CTkButton(
            self, text="Advanced Settings  +", font=ctk.CTkFont(size=11),
            fg_color="transparent", hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"], anchor="w",
            command=self._toggle_advanced,
        )
        self._adv_toggle.pack(padx=16, pady=(0, 4), fill="x")

        self._adv_frame = ctk.CTkFrame(self, fg_color="transparent")

        ctk.CTkLabel(self._adv_frame, text="Temperature", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(padx=0, anchor="w")
        self.temp_slider = ctk.CTkSlider(
            self._adv_frame, from_=0, to=1, number_of_steps=20,
            button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"],
        )
        self.temp_slider.set(0.2)
        self.temp_slider.pack(fill="x", pady=(2, 6))

        ctk.CTkLabel(self._adv_frame, text="Top-K Chunks", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.topk_entry = ctk.CTkEntry(
            self._adv_frame, fg_color=COLORS["bg_input"], border_color=COLORS["border"],
        )
        self.topk_entry.insert(0, "5")
        self.topk_entry.pack(fill="x", pady=(2, 6))

        ctk.CTkLabel(self._adv_frame, text="Chunk Size (tokens)", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.chunk_entry = ctk.CTkEntry(
            self._adv_frame, fg_color=COLORS["bg_input"], border_color=COLORS["border"],
        )
        self.chunk_entry.insert(0, "512")
        self.chunk_entry.pack(fill="x", pady=(2, 6))

        ctk.CTkLabel(self._adv_frame, text="Embedding Model", font=ctk.CTkFont(size=11),
                      text_color=COLORS["text_secondary"]).pack(anchor="w")
        self.embed_var = ctk.StringVar(value=EMBEDDING_MODELS[0])
        ctk.CTkOptionMenu(
            self._adv_frame, variable=self.embed_var, values=EMBEDDING_MODELS,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"],
        ).pack(fill="x", pady=(2, 6))

        self._sep()

        # ── Stats ──
        self._section("KNOWLEDGE BASE")
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.pack(padx=16, fill="x", pady=(0, 8))
        stats.grid_columnconfigure((0, 1, 2), weight=1)

        self.stat_files = self._stat_card(stats, "0", "Files", 0)
        self.stat_dbs = self._stat_card(stats, "0", "DBs", 1)
        self.stat_indexed = self._stat_card(stats, "0", "Indexed", 2)

        # ── Status ──
        self.status_label = ctk.CTkLabel(
            self, text="  API key not set", font=ctk.CTkFont(size=12),
            text_color=COLORS["warning"], anchor="w",
        )
        self.status_label.pack(padx=16, pady=(4, 8), anchor="w")
        self.api_key_entry.bind("<KeyRelease>", self._on_key_change)

        self._sep()
        ctk.CTkLabel(
            self, text="v0.1.0  |  Hybrid RAG UI",
            font=ctk.CTkFont(size=10), text_color=COLORS["text_muted"],
        ).pack(padx=16, pady=(4, 16), anchor="w")

    # ── helpers ──────────────────────────────────────────────────────────────
    def _section(self, text: str):
        ctk.CTkLabel(
            self, text=text,
            font=ctk.CTkFont(size=10, weight="bold"), text_color=COLORS["text_muted"],
        ).pack(padx=16, pady=(8, 4), anchor="w")

    def _sep(self):
        ctk.CTkFrame(self, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=16, pady=8)

    def _stat_card(self, parent, value, label, col):
        frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_card"], corner_radius=8)
        frame.grid(row=0, column=col, padx=3, sticky="ew")
        val_lbl = ctk.CTkLabel(
            frame, text=value, font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_primary"],
        )
        val_lbl.pack(pady=(8, 0))
        ctk.CTkLabel(
            frame, text=label, font=ctk.CTkFont(size=9), text_color=COLORS["text_muted"],
        ).pack(pady=(0, 8))
        return val_lbl

    def _toggle_advanced(self):
        self._adv_visible = not self._adv_visible
        if self._adv_visible:
            self._adv_frame.pack(padx=16, fill="x", after=self._adv_toggle)
            self._adv_toggle.configure(text="Advanced Settings  -")
        else:
            self._adv_frame.pack_forget()
            self._adv_toggle.configure(text="Advanced Settings  +")

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
            self.status_label.configure(
                text=f"  {p} connected  |  {m}", text_color=COLORS["success"],
            )
        else:
            self.status_label.configure(
                text="  API key not set", text_color=COLORS["warning"],
            )

    # ── public API ───────────────────────────────────────────────────────────
    def refresh_stats(self, n_files: int, n_dbs: int, n_indexed: int):
        self.stat_files.configure(text=str(n_files))
        self.stat_dbs.configure(text=str(n_dbs))
        self.stat_indexed.configure(text=str(n_indexed))
