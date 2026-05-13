"""
mcp_server.py
MCP server using FastMCP — works with  uv run mcp dev mcp_server.py
"""

from mcp.server.fastmcp import FastMCP
from core.documents import list_documents, read_document, edit_document

mcp = FastMCP("doc-server")


@mcp.resource("doc://{name}")
def get_document(name: str) -> str:
    """Expose a document as an MCP resource."""
    return read_document(name)


@mcp.tool()
def read_document_tool(name: str) -> str:
    """Read the full text content of a document from the collection."""
    try:
        return read_document(name)
    except FileNotFoundError as e:
        return str(e)


@mcp.tool()
def edit_document_tool(name: str, content: str) -> str:
    """Create or overwrite a document in the collection."""
    return edit_document(name, content)


@mcp.tool()
def list_documents_tool() -> list[str]:
    """List all documents in the collection."""
    return list_documents()


if __name__ == "__main__":
    mcp.run()
