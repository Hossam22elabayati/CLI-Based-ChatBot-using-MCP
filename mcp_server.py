"""
mcp_server.py
MCP server that exposes two tools:
  - read_document  : read a file from the documents collection
  - edit_document  : write / overwrite a file in the documents collection

Run with:
    python mcp_server.py
"""

import asyncio
import json
import sys
from core.documents import list_documents, read_document, edit_document

# ---------------------------------------------------------------------------
# Tiny MCP protocol helpers (JSON-RPC 2.0 over stdin/stdout)
# ---------------------------------------------------------------------------

def _send(obj: dict):
    line = json.dumps(obj)
    sys.stdout.write(line + "\n")
    sys.stdout.flush()


def _reply(req_id, result):
    _send({"jsonrpc": "2.0", "id": req_id, "result": result})


def _error(req_id, code: int, message: str):
    _send({"jsonrpc": "2.0", "id": req_id,
           "error": {"code": code, "message": message}})


# ---------------------------------------------------------------------------
# Tool definitions (returned on initialize / tools/list)
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "read_document",
        "description": "Read the full text content of a document from the collection.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The filename of the document to read (e.g. 'notes.txt')."
                }
            },
            "required": ["name"]
        }
    },
    {
        "name": "edit_document",
        "description": (
            "Create or overwrite a document in the collection with the given content. "
            "If the document does not exist it will be created."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The filename of the document to create or overwrite."
                },
                "content": {
                    "type": "string",
                    "description": "The new full text content of the document."
                }
            },
            "required": ["name", "content"]
        }
    },
]


# ---------------------------------------------------------------------------
# Request dispatcher
# ---------------------------------------------------------------------------

def _handle(req: dict) -> None:
    method = req.get("method")
    req_id = req.get("id")
    params = req.get("params", {})

    # --- Handshake --------------------------------------------------------
    if method == "initialize":
        _reply(req_id, {
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "doc-server", "version": "1.0.0"}
        })

    elif method == "initialized":
        pass  # notification, no reply needed

    # --- Tool discovery ---------------------------------------------------
    elif method == "tools/list":
        _reply(req_id, {"tools": TOOLS})

    # --- Tool execution ---------------------------------------------------
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        try:
            if tool_name == "read_document":
                name = args["name"]
                content = read_document(name)
                _reply(req_id, {
                    "content": [{"type": "text", "text": content}]
                })

            elif tool_name == "edit_document":
                name = args["name"]
                new_content = args["content"]
                msg = edit_document(name, new_content)
                _reply(req_id, {
                    "content": [{"type": "text", "text": msg}]
                })

            else:
                _error(req_id, -32601, f"Unknown tool: {tool_name}")

        except FileNotFoundError as exc:
            _reply(req_id, {
                "content": [{"type": "text", "text": str(exc)}],
                "isError": True
            })
        except KeyError as exc:
            _error(req_id, -32602, f"Missing argument: {exc}")

    # --- Resources (list documents) ---------------------------------------
    elif method == "resources/list":
        docs = list_documents()
        resources = [
            {"uri": f"doc://{name}", "name": name, "mimeType": "text/plain"}
            for name in docs
        ]
        _reply(req_id, {"resources": resources})

    # --- Unknown method ---------------------------------------------------
    elif req_id is not None:
        _error(req_id, -32601, f"Method not found: {method}")


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            req = json.loads(raw_line)
        except json.JSONDecodeError:
            _send({"jsonrpc": "2.0", "id": None,
                   "error": {"code": -32700, "message": "Parse error"}})
            continue
        _handle(req)


if __name__ == "__main__":
    main()
