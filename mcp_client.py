"""
mcp_client.py
MCP client using the official `mcp` SDK (ClientSession).
Runs the entire session inside a single asyncio event loop to avoid
anyio cancel-scope teardown issues.
"""

import asyncio
import concurrent.futures
import threading
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = Path(__file__).parent / "mcp_server.py"


class MCPClient:
    """
    Sync wrapper around the async MCP ClientSession.
    All calls run inside one persistent event loop thread.
    """

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._session: ClientSession | None = None
        self._call_queue: asyncio.Queue = None
        self._started = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self):
        """Start the server subprocess and complete the MCP handshake."""
        ready = threading.Event()
        error_box = []

        def run():
            asyncio.set_event_loop(self._loop)
            self._loop.run_until_complete(self._session_loop(ready, error_box))

        t = threading.Thread(target=run, daemon=True)
        t.start()
        ready.wait(timeout=10)
        if error_box:
            raise RuntimeError(error_box[0])
        self._started = True

    async def _session_loop(self, ready, error_box):
        """Owns the full MCP session lifetime."""
        self._call_queue = asyncio.Queue()
        server_params = StdioServerParameters(
            command="python",
            args=[str(SERVER_SCRIPT)],
        )
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self._session = session
                    await session.initialize()
                    ready.set()
                    while True:
                        fut, coro = await self._call_queue.get()
                        if coro is None:        # stop sentinel
                            fut.set_result(None)
                            break
                        try:
                            result = await coro
                            fut.set_result(result)
                        except Exception as exc:
                            fut.set_exception(exc)
        except Exception as exc:
            error_box.append(str(exc))
            ready.set()

    def stop(self):
        if self._call_queue:
            self._loop.call_soon_threadsafe(
                lambda: asyncio.ensure_future(self._send_stop(), loop=self._loop)
            )

    async def _send_stop(self):
        future = self._loop.create_future()
        await self._call_queue.put((future, None))

    def _run(self, coro):
        """Submit a coroutine to the session loop and block until result."""
        future = self._loop.create_future()

        async def enqueue():
            await self._call_queue.put((future, coro))

        asyncio.run_coroutine_threadsafe(enqueue(), self._loop)

        cf = concurrent.futures.Future()

        def on_done(f):
            try:
                cf.set_result(f.result())
            except Exception as e:
                cf.set_exception(e)

        self._loop.call_soon_threadsafe(future.add_done_callback, on_done)
        return cf.result(timeout=15)

    # ------------------------------------------------------------------
    # High-level helpers (called by main.py)
    # ------------------------------------------------------------------

    def list_tools(self) -> list[dict]:
        result = self._run(self._session.list_tools())
        return [{"name": t.name, "description": t.description} for t in result.tools]

    def list_documents(self) -> list[str]:
        result = self._run(
            self._session.call_tool("list_documents_tool", {})
        )
        import json
        return json.loads(result.content[0].text)

    def read_document(self, name: str) -> str:
        result = self._run(
            self._session.call_tool("read_document_tool", {"name": name})
        )
        return result.content[0].text

    def edit_document(self, name: str, content: str) -> str:
        result = self._run(
            self._session.call_tool(
                "edit_document_tool", {"name": name, "content": content}
            )
        )
        return result.content[0].text
