"""
core/documents.py
Handles the in-memory document collection used by the MCP server.
"""

import os
import json
from pathlib import Path

DOCS_DIR = Path(__file__).parent.parent / "documents"


def ensure_docs_dir():
    DOCS_DIR.mkdir(exist_ok=True)


def list_documents() -> list[str]:
    """Return the names of all documents in the collection."""
    ensure_docs_dir()
    return [f.name for f in DOCS_DIR.iterdir() if f.is_file()]


def read_document(name: str) -> str:
    """Read and return the content of a document by name."""
    ensure_docs_dir()
    path = DOCS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Document '{name}' does not exist.")
    return path.read_text(encoding="utf-8")


def edit_document(name: str, new_content: str) -> str:
    """Overwrite a document with new content. Creates it if it doesn't exist."""
    ensure_docs_dir()
    path = DOCS_DIR / name
    path.write_text(new_content, encoding="utf-8")
    return f"Document '{name}' saved successfully."
