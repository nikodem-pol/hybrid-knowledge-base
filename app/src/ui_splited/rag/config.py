"""
Shared constants: colors, supported file types, model lists, embedding models.
"""

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
    ("PDF", "*.pdf"),
    ("Text", "*.txt"),
    ("Markdown", "*.md"),
    ("HTML", "*.html *.htm"),
    ("CSV", "*.csv"),
    ("JSON", "*.json"),
    ("XML", "*.xml"),
    ("DOCX", "*.docx"),
    ("RST", "*.rst"),
    ("Log", "*.log"),
]

LLM_MODELS = {
    "OpenAI": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1-preview", "o1-mini"],
    "Anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-3.5-sonnet"],
    "Google": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
    "Mistral": ["mistral-large", "mistral-medium", "mistral-small", "mixtral-8x7b"],
    "Groq": ["llama-3-70b", "llama-3-8b", "mixtral-8x7b", "gemma-7b"],
    "Local / Ollama": ["llama3", "mistral", "phi3", "gemma", "codellama", "custom"],
}

EMBEDDING_MODELS = [
    "text-embedding-3-small",
    "text-embedding-3-large",
    "text-embedding-ada-002",
    "all-MiniLM-L6-v2 (local)",
    "nomic-embed-text (local)",
]
