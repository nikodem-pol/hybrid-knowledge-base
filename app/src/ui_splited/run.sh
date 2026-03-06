#!/usr/bin/env bash
# ─────────────────────────────────────────────────────
#  RAG Knowledge Base — Desktop App Launcher
# ─────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "══════════════════════════════════════════════"
echo "  RAG Knowledge Base — Desktop App"
echo "══════════════════════════════════════════════"
echo ""

if ! command -v python3 &>/dev/null; then
    echo "Error: python3 is not installed."
    exit 1
fi

VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "-> Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"

echo "-> Installing dependencies..."
pip install -q -r "$SCRIPT_DIR/requirements.txt"

echo ""
echo "-> Launching desktop app..."
python "$SCRIPT_DIR/rag_ui.py"
