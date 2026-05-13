"""
mcp_client.py
Thin MCP client that launches mcp_server.py as a subprocess and
communicates with it over stdin/stdout using JSON-RPC 2.0.
"""

import json
import subprocess
import sys
import threading
from pathlib import Path

SERVER_SCRIPT = Path(__file__).parent / "mcp_server.py"


class MCPClient:
    def __init__(self):
        self._proc = None
        self._id_counter = 0
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        """Launch the MCP server subprocess."""
        self._proc = subprocess.Popen(
            [sys.executable, str(SERVER_SCRIPT)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        # Perform MCP handshake
        self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "doc-client", "version": "1.0.0"}
        })
        self._send_notification("initialized")

    def stop(self):
        if self._proc:
            self._proc.terminate()
            self._proc = None

    # ------------------------------------------------------------------
    # Low-level transport
    # ------------------------------------------------------------------

    def _next_id(self) -> int:
        with self._lock:
            self._id_counter += 1
            return self._id_counter

    def _send(self, method: str, params: dict = None) -> dict:
        """Send a request and wait for the matching response."""
        req_id = self._next_id()
        msg = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params:
            msg["params"] = params

        line = json.dumps(msg) + "\n"
        self._proc.stdin.write(line)
        self._proc.stdin.flush()

        # Read lines until we get our response id
        while True:
            raw = self._proc.stdout.readline()
            if not raw:
                raise RuntimeError("MCP server closed unexpectedly.")
            raw = raw.strip()
            if not raw:
                continue
            resp = json.loads(raw)
            if resp.get("id") == req_id:
                if "error" in resp:
                    raise RuntimeError(resp["error"]["message"])
                return resp.get("result", {})

    def _send_notification(self, method: str, params: dict = None):
        """Send a notification (no id, no reply expected)."""
        msg = {"jsonrpc": "2.0", "method": method}
        if params:
            msg["params"] = params
        line = json.dumps(msg) + "\n"
        self._proc.stdin.write(line)
        self._proc.stdin.flush()

    # ------------------------------------------------------------------
    # High-level MCP operations
    # ------------------------------------------------------------------

    def list_tools(self) -> list[dict]:
        result = self._send("tools/list")
        return result.get("tools", [])

    def list_documents(self) -> list[str]:
        result = self._send("resources/list")
        return [r["name"] for r in result.get("resources", [])]

    def read_document(self, name: str) -> str:
        result = self._send("tools/call", {
            "name": "read_document",
            "arguments": {"name": name}
        })
        return result["content"][0]["text"]

    def edit_document(self, name: str, content: str) -> str:
        result = self._send("tools/call", {
            "name": "edit_document",
            "arguments": {"name": name, "content": content}
        })
        return result["content"][0]["text"]
