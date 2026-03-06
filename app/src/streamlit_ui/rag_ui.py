"""
Hybrid RAG Knowledge Base — Lightweight Streamlit UI
=====================================================
Run:  streamlit run scripts/rag_ui.py
"""

import streamlit as st
import os
import json
import hashlib
from pathlib import Path
from datetime import datetime

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RAG Knowledge Base",
    page_icon="brain",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

[data-testid="stAppViewContainer"] {
    font-family: 'Inter', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stNumberInput label {
    color: #94a3b8 !important;
    font-size: 0.8rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

[data-testid="stSidebar"] hr {
    border-color: #334155;
}

/* ── Cards ── */
.source-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
    transition: box-shadow 0.2s;
}
.source-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.db-card {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

.file-card {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.75rem;
}

/* ── Status badges ── */
.badge {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.badge-ready   { background: #dcfce7; color: #166534; }
.badge-pending { background: #fef9c3; color: #854d0e; }
.badge-error   { background: #fee2e2; color: #991b1b; }
.badge-file    { background: #dbeafe; color: #1e40af; }
.badge-db      { background: #d1fae5; color: #065f46; }

/* ── Chat bubbles ── */
.chat-user {
    background: #1e293b;
    color: #f1f5f9;
    padding: 0.85rem 1.15rem;
    border-radius: 16px 16px 4px 16px;
    margin: 0.5rem 0;
    max-width: 80%;
    margin-left: auto;
    font-size: 0.92rem;
    line-height: 1.5;
}

.chat-assistant {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #1e293b;
    padding: 0.85rem 1.15rem;
    border-radius: 16px 16px 16px 4px;
    margin: 0.5rem 0;
    max-width: 80%;
    font-size: 0.92rem;
    line-height: 1.5;
}

.chat-sources {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.5rem;
    padding-top: 0.5rem;
    border-top: 1px solid #e2e8f0;
}

/* ── Section headers ── */
.section-header {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 0.75rem;
}

/* ── Metric cards ── */
.metric-row {
    display: flex;
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
.metric-card {
    flex: 1;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    text-align: center;
}
.metric-card .value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #0f172a;
}
.metric-card .label {
    font-size: 0.7rem;
    font-weight: 500;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Upload zone ── */
[data-testid="stFileUploader"] {
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    background: #f8fafc !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #3b82f6 !important;
    background: #eff6ff !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.25rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-weight: 500;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ── Session state defaults ───────────────────────────────────────────────────
DEFAULTS = {
    "chat_history": [],
    "uploaded_files": [],
    "db_connections": [],
    "llm_provider": "OpenAI",
    "api_key": "",
    "model": "gpt-4o",
    "temperature": 0.2,
    "indexing_status": {},
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v if not isinstance(v, (list, dict)) else type(v)(v)


# ── Helpers ──────────────────────────────────────────────────────────────────
SUPPORTED_FILE_TYPES = ["pdf", "txt", "md", "html", "htm", "csv", "json", "xml", "docx", "rst", "log"]

FILE_TYPE_ICONS = {
    "pdf": "📕", "txt": "📄", "md": "📝", "html": "🌐", "htm": "🌐",
    "csv": "📊", "json": "🔧", "xml": "📋", "docx": "📘", "rst": "📓", "log": "📜",
}

DB_TYPE_DEFAULTS = {
    "SQLite":      {"host": "", "port": "", "database": "path/to/database.db", "user": "", "password": ""},
    "PostgreSQL":  {"host": "localhost", "port": "5432", "database": "mydb", "user": "postgres", "password": ""},
    "MySQL":       {"host": "localhost", "port": "3306", "database": "mydb", "user": "root", "password": ""},
}

LLM_MODELS = {
    "OpenAI":    ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo", "o1-preview", "o1-mini"],
    "Anthropic": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku", "claude-3.5-sonnet"],
    "Google":    ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
    "Mistral":   ["mistral-large", "mistral-medium", "mistral-small", "mixtral-8x7b"],
    "Groq":      ["llama-3-70b", "llama-3-8b", "mixtral-8x7b", "gemma-7b"],
    "Local / Ollama": ["llama3", "mistral", "phi3", "gemma", "codellama", "custom"],
}


def file_hash(name: str, size: int) -> str:
    return hashlib.md5(f"{name}{size}".encode()).hexdigest()[:10]


def format_size(size_bytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


# ── Sidebar: LLM Configuration ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("### :brain: RAG Knowledge Base")
    st.caption("Hybrid retrieval from files & databases")
    st.divider()

    # -- LLM Provider ---
    st.markdown('<p class="section-header">LLM Configuration</p>', unsafe_allow_html=True)

    provider = st.selectbox(
        "Provider",
        list(LLM_MODELS.keys()),
        index=list(LLM_MODELS.keys()).index(st.session_state.llm_provider),
        key="sel_provider",
    )
    st.session_state.llm_provider = provider

    model = st.selectbox("Model", LLM_MODELS[provider], key="sel_model")
    st.session_state.model = model

    api_key = st.text_input(
        "API Key" if provider != "Local / Ollama" else "Endpoint URL",
        value=st.session_state.api_key,
        type="password" if provider != "Local / Ollama" else "default",
        placeholder="sk-..." if provider == "OpenAI" else "Enter key or URL",
        key="inp_api_key",
    )
    st.session_state.api_key = api_key

    with st.expander("Advanced LLM Settings", expanded=False):
        st.session_state.temperature = st.slider("Temperature", 0.0, 1.0, st.session_state.temperature, 0.05)
        max_tokens = st.number_input("Max tokens", 256, 128_000, 4096, step=256)
        top_k = st.number_input("Top-K retrieval chunks", 1, 50, 5)
        chunk_size = st.number_input("Chunk size (tokens)", 128, 4096, 512, step=64)
        chunk_overlap = st.number_input("Chunk overlap (tokens)", 0, 512, 50, step=10)
        embedding_model = st.selectbox("Embedding model", [
            "text-embedding-3-small", "text-embedding-3-large",
            "text-embedding-ada-002", "all-MiniLM-L6-v2 (local)",
            "nomic-embed-text (local)",
        ])

    st.divider()

    # -- Quick stats --
    n_files = len(st.session_state.uploaded_files)
    n_dbs   = len(st.session_state.db_connections)
    n_ready = sum(1 for v in st.session_state.indexing_status.values() if v == "ready")

    st.markdown('<p class="section-header">Knowledge Base Stats</p>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="value">{n_files}</div><div class="label">Files</div></div>
        <div class="metric-card"><div class="value">{n_dbs}</div><div class="label">Databases</div></div>
        <div class="metric-card"><div class="value">{n_ready}</div><div class="label">Indexed</div></div>
    </div>
    """, unsafe_allow_html=True)

    key_set = bool(api_key.strip())
    if key_set:
        st.success(f"**{provider}** connected  ·  `{model}`", icon="✅")
    else:
        label = "API key" if provider != "Local / Ollama" else "Endpoint"
        st.warning(f"{label} not set", icon="⚠️")

    st.divider()
    st.caption("v0.1.0  ·  Hybrid RAG UI")


# ── Main area ────────────────────────────────────────────────────────────────
tab_chat, tab_files, tab_databases, tab_sources = st.tabs([
    "💬  Chat", "📁  Files", "🗄️  Databases", "📚  Sources Overview",
])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — CHAT
# ══════════════════════════════════════════════════════════════════════════════
with tab_chat:
    st.markdown("#### Ask your knowledge base")
    st.caption("Questions are answered using both uploaded files and connected databases.")

    # ── Chat history ──
    chat_container = st.container(height=520)
    with chat_container:
        if not st.session_state.chat_history:
            st.markdown("""
            <div style="
                display:flex; flex-direction:column; align-items:center; justify-content:center;
                height:100%; min-height: 400px; color:#94a3b8; text-align:center;
            ">
                <div style="font-size:3rem; margin-bottom:0.5rem;">🧠</div>
                <div style="font-size:1.1rem; font-weight:600; color:#475569;">
                    Your knowledge base is ready
                </div>
                <div style="font-size:0.85rem; margin-top:0.35rem; max-width:28rem; line-height:1.5;">
                    Upload files or connect databases in the other tabs,
                    then come back here to ask questions about your data.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            for msg in st.session_state.chat_history:
                if msg["role"] == "user":
                    st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    sources_html = ""
                    if msg.get("sources"):
                        src_items = " · ".join(msg["sources"])
                        sources_html = f'<div class="chat-sources">Sources: {src_items}</div>'
                    st.markdown(
                        f'<div class="chat-assistant">{msg["content"]}{sources_html}</div>',
                        unsafe_allow_html=True,
                    )

    # ── Input row ──
    col_input, col_btn = st.columns([6, 1])
    with col_input:
        user_query = st.text_input(
            "Query",
            placeholder="Ask a question about your knowledge base...",
            label_visibility="collapsed",
            key="chat_input",
        )
    with col_btn:
        send_clicked = st.button("Send", use_container_width=True, type="primary")

    if send_clicked and user_query.strip():
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        # ── Placeholder response (replace with actual RAG call) ──
        source_labels = [f["name"] for f in st.session_state.uploaded_files[:2]]
        source_labels += [c["name"] for c in st.session_state.db_connections[:1]]
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": (
                f"*[This is a placeholder response.]*\n\n"
                f"Your question **\"{user_query}\"** would be answered by:\n"
                f"1. Embedding the query with **{embedding_model}**\n"
                f"2. Retrieving the top-**{top_k}** chunks from **{n_files}** file(s) "
                f"and querying **{n_dbs}** database(s)\n"
                f"3. Generating an answer with **{provider} / {model}** "
                f"(temp={st.session_state.temperature})\n\n"
                f"Connect your RAG backend to replace this stub."
            ),
            "sources": source_labels if source_labels else ["No sources loaded yet"],
        })
        st.rerun()

    # Quick-action chips
    st.markdown('<p class="section-header" style="margin-top:0.75rem">Suggestions</p>', unsafe_allow_html=True)
    chip_cols = st.columns(4)
    suggestions = [
        "Summarize all loaded documents",
        "What tables exist in my database?",
        "Compare info across file and DB sources",
        "List key entities mentioned in my data",
    ]
    for i, s in enumerate(suggestions):
        if chip_cols[i].button(s, key=f"chip_{i}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": s})
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": f"*[Placeholder]* Would process: **{s}**",
                "sources": [],
            })
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — FILE UPLOAD
# ══════════════════════════════════════════════════════════════════════════════
with tab_files:
    st.markdown("#### Upload Documents")
    st.caption("Supported formats: PDF, TXT, Markdown, HTML, CSV, JSON, XML, DOCX, RST, LOG")

    uploaded = st.file_uploader(
        "Drop files here",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded:
        for f in uploaded:
            fid = file_hash(f.name, f.size)
            if not any(x["id"] == fid for x in st.session_state.uploaded_files):
                ext = f.name.rsplit(".", 1)[-1].lower() if "." in f.name else "txt"
                st.session_state.uploaded_files.append({
                    "id": fid,
                    "name": f.name,
                    "size": f.size,
                    "type": ext,
                    "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                st.session_state.indexing_status[fid] = "pending"

    if st.session_state.uploaded_files:
        # ── Toolbar ──
        tool_col1, tool_col2, tool_col3 = st.columns([2, 2, 1])
        with tool_col1:
            if st.button("🔄  Index All Pending", use_container_width=True):
                for f in st.session_state.uploaded_files:
                    if st.session_state.indexing_status.get(f["id"]) == "pending":
                        st.session_state.indexing_status[f["id"]] = "ready"
                st.rerun()
        with tool_col2:
            if st.button("🗑️  Remove All Files", use_container_width=True, type="secondary"):
                st.session_state.uploaded_files.clear()
                st.session_state.indexing_status.clear()
                st.rerun()

        st.markdown("---")

        # ── File list ──
        for f in st.session_state.uploaded_files:
            status = st.session_state.indexing_status.get(f["id"], "pending")
            badge_cls = {"ready": "badge-ready", "pending": "badge-pending", "error": "badge-error"}[status]
            icon = FILE_TYPE_ICONS.get(f["type"], "📄")

            c1, c2, c3, c4 = st.columns([0.5, 3, 1.5, 1])
            with c1:
                st.markdown(f"<div style='font-size:1.5rem;text-align:center;padding-top:0.3rem'>{icon}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"**{f['name']}**")
                st.caption(f"{format_size(f['size'])}  ·  Uploaded {f['uploaded_at']}")
            with c3:
                st.markdown(
                    f'<span class="badge {badge_cls}">{status}</span>',
                    unsafe_allow_html=True,
                )
            with c4:
                if st.button("✕", key=f"rm_{f['id']}", help="Remove file"):
                    st.session_state.uploaded_files = [x for x in st.session_state.uploaded_files if x["id"] != f["id"]]
                    st.session_state.indexing_status.pop(f["id"], None)
                    st.rerun()
    else:
        st.info("No files uploaded yet. Drag & drop files above to get started.", icon="📂")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — DATABASE CONNECTIONS
# ══════════════════════════════════════════════════════════════════════════════
with tab_databases:
    st.markdown("#### Connect Databases")
    st.caption("Add SQL databases so the RAG system can query structured data.")

    with st.expander("➕  Add New Connection", expanded=not st.session_state.db_connections):
        db_col1, db_col2 = st.columns(2)
        with db_col1:
            conn_name = st.text_input("Connection name", placeholder="e.g. Production DB")
            db_type = st.selectbox("Database type", list(DB_TYPE_DEFAULTS.keys()))
        with db_col2:
            defaults = DB_TYPE_DEFAULTS[db_type]
            if db_type == "SQLite":
                db_path = st.text_input("Database file path", value=defaults["database"],
                                        placeholder="/path/to/database.db")
            else:
                db_host = st.text_input("Host", value=defaults["host"])
                db_port = st.text_input("Port", value=defaults["port"])

        if db_type != "SQLite":
            db_col3, db_col4 = st.columns(2)
            with db_col3:
                db_name = st.text_input("Database name", value=defaults["database"])
                db_user = st.text_input("Username", value=defaults["user"])
            with db_col4:
                db_pass = st.text_input("Password", type="password", value=defaults["password"])
                db_ssl  = st.checkbox("Use SSL", value=False)

        # -- Optional: restrict which tables/schemas the RAG can see --
        with st.container():
            st.markdown('<p class="section-header">Access Scope (optional)</p>', unsafe_allow_html=True)
            scope_col1, scope_col2 = st.columns(2)
            with scope_col1:
                schemas = st.text_input("Schemas (comma-separated)", placeholder="public, analytics")
            with scope_col2:
                tables = st.text_input("Tables (comma-separated)", placeholder="users, orders, products")

            natural_lang_desc = st.text_area(
                "Describe this database (helps the LLM write better queries)",
                placeholder="e.g. This is our e-commerce database containing customer orders, product catalog, and inventory levels.",
                height=80,
            )

        btn_col1, btn_col2 = st.columns([1, 3])
        with btn_col1:
            add_db = st.button("Add Connection", type="primary", use_container_width=True)
        with btn_col2:
            test_db = st.button("🔌  Test Connection", use_container_width=True)

        if test_db:
            st.info("Connection test placeholder — wire up your DB driver here.", icon="🔌")

        if add_db and conn_name.strip():
            conn = {
                "id": hashlib.md5(f"{conn_name}{datetime.now()}".encode()).hexdigest()[:10],
                "name": conn_name,
                "type": db_type,
                "connected_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "description": natural_lang_desc,
                "schemas": [s.strip() for s in schemas.split(",") if s.strip()] if schemas else [],
                "tables": [t.strip() for t in tables.split(",") if t.strip()] if tables else [],
            }
            if db_type == "SQLite":
                conn["path"] = db_path
            else:
                conn["host"] = db_host
                conn["port"] = db_port
                conn["database"] = db_name
                conn["user"] = db_user

            st.session_state.db_connections.append(conn)
            st.session_state.indexing_status[conn["id"]] = "ready"
            st.success(f"Added **{conn_name}** ({db_type})")
            st.rerun()

    # ── Existing connections list ──
    if st.session_state.db_connections:
        st.markdown("---")
        st.markdown('<p class="section-header">Active Connections</p>', unsafe_allow_html=True)

        for conn in st.session_state.db_connections:
            with st.container():
                c1, c2, c3 = st.columns([4, 1.5, 0.5])
                with c1:
                    location = conn.get("path") or f'{conn.get("host","?")}:{conn.get("port","?")}/{conn.get("database","?")}'
                    st.markdown(f"""
                    <div class="db-card">
                        <strong>🗄️ {conn['name']}</strong>
                        <span class="badge badge-db" style="margin-left:0.5rem">{conn['type']}</span><br>
                        <span style="font-size:0.8rem;color:#64748b">{location}</span>
                        {f'<br><span style="font-size:0.78rem;color:#64748b;font-style:italic">{conn["description"]}</span>' if conn.get("description") else ""}
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    scope_parts = []
                    if conn.get("schemas"):
                        scope_parts.append(f"Schemas: {', '.join(conn['schemas'])}")
                    if conn.get("tables"):
                        scope_parts.append(f"Tables: {', '.join(conn['tables'])}")
                    if scope_parts:
                        st.caption("\n".join(scope_parts))
                    else:
                        st.caption("Full access")
                with c3:
                    if st.button("✕", key=f"rm_db_{conn['id']}", help="Remove connection"):
                        st.session_state.db_connections = [
                            c for c in st.session_state.db_connections if c["id"] != conn["id"]
                        ]
                        st.session_state.indexing_status.pop(conn["id"], None)
                        st.rerun()
    else:
        st.info("No databases connected. Use the form above to add one.", icon="🗄️")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — SOURCES OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_sources:
    st.markdown("#### Knowledge Base Sources")
    st.caption("Overview of all data sources powering the RAG system.")

    all_sources = []
    for f in st.session_state.uploaded_files:
        status = st.session_state.indexing_status.get(f["id"], "pending")
        all_sources.append({
            "kind": "file", "name": f["name"], "detail": format_size(f["size"]),
            "status": status, "added": f["uploaded_at"], "id": f["id"],
        })
    for c in st.session_state.db_connections:
        loc = c.get("path") or f'{c.get("host","")}:{c.get("port","")}/{c.get("database","")}'
        all_sources.append({
            "kind": "db", "name": c["name"], "detail": f"{c['type']} — {loc}",
            "status": "ready", "added": c["connected_at"], "id": c["id"],
        })

    if all_sources:
        # ── Filter bar ──
        filt_col1, filt_col2, filt_col3 = st.columns([2, 2, 2])
        with filt_col1:
            kind_filter = st.selectbox("Type", ["All", "Files", "Databases"], key="filt_kind")
        with filt_col2:
            status_filter = st.selectbox("Status", ["All", "Ready", "Pending"], key="filt_status")
        with filt_col3:
            search_filter = st.text_input("Search", placeholder="Filter by name...", key="filt_search")

        filtered = all_sources
        if kind_filter == "Files":
            filtered = [s for s in filtered if s["kind"] == "file"]
        elif kind_filter == "Databases":
            filtered = [s for s in filtered if s["kind"] == "db"]
        if status_filter != "All":
            filtered = [s for s in filtered if s["status"] == status_filter.lower()]
        if search_filter:
            filtered = [s for s in filtered if search_filter.lower() in s["name"].lower()]

        st.markdown(f"Showing **{len(filtered)}** of {len(all_sources)} sources")
        st.markdown("---")

        for src in filtered:
            badge_cls = "badge-file" if src["kind"] == "file" else "badge-db"
            status_cls = {"ready": "badge-ready", "pending": "badge-pending", "error": "badge-error"}[src["status"]]
            kind_label = "FILE" if src["kind"] == "file" else "DATABASE"

            st.markdown(f"""
            <div class="source-card" style="display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <span class="badge {badge_cls}">{kind_label}</span>
                    <strong style="margin-left:0.5rem">{src['name']}</strong><br>
                    <span style="font-size:0.8rem;color:#64748b">{src['detail']}  ·  Added {src['added']}</span>
                </div>
                <span class="badge {status_cls}">{src['status']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:3rem;color:#94a3b8">
            <div style="font-size:2.5rem;margin-bottom:0.5rem">📚</div>
            <div style="font-size:1rem;font-weight:600;color:#475569">No sources yet</div>
            <div style="font-size:0.85rem;margin-top:0.25rem">
                Upload files or connect databases to populate your knowledge base.
            </div>
        </div>
        """, unsafe_allow_html=True)
