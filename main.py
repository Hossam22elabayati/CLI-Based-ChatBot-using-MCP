"""
main.py
CLI chatbot that lets users manage a collection of documents.
The chatbot uses the MCP client to talk to mcp_server.py, which
exposes two tools:  read_document  and  edit_document.

Usage:
    python main.py
"""

import sys
from mcp_client import MCPClient

BANNER = """
╔══════════════════════════════════════════════╗
║         📄  Document Chatbot (MCP)           ║
║  Type  help  to see available commands.      ║
╚══════════════════════════════════════════════╝
"""

HELP_TEXT = """
Available commands
──────────────────
  list                    Show all documents in the collection
  read  <filename>        Print the content of a document
  edit  <filename>        Open an interactive editor to write/update a doc
  new   <filename>        Alias for  edit  (creates the file if missing)
  tools                   List the MCP tools exposed by the server
  help                    Show this message
  exit / quit             Exit the chatbot
"""


# ---------------------------------------------------------------------------
# Interactive multi-line editor
# ---------------------------------------------------------------------------

def interactive_editor(existing_content: str = "") -> str:
    """
    Tiny in-terminal editor.
    The user types lines; an empty line followed by EOF (Ctrl-D / Ctrl-Z)
    or the sentinel  !save  saves the document.
    """
    print("\n  ┌─ Editor ──────────────────────────────────────────┐")
    print("  │  Type your content. Enter  !save  on a blank line │")
    print("  │  to save, or Ctrl-C to cancel.                    │")
    print("  └────────────────────────────────────────────────────┘")

    if existing_content:
        print("\n  [Current content shown below — it will be replaced]\n")
        for line in existing_content.splitlines():
            print(f"  > {line}")
        print()

    lines = []
    try:
        while True:
            line = input("  | ")
            if line.strip() == "!save":
                break
            lines.append(line)
    except (KeyboardInterrupt, EOFError):
        print("\n  [Cancelled]")
        return None

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_list(client: MCPClient):
    docs = client.list_documents()
    if not docs:
        print("  (no documents yet — use  new <filename>  to create one)")
    else:
        print(f"\n  📁  {len(docs)} document(s):\n")
        for name in sorted(docs):
            print(f"      • {name}")
    print()


def cmd_read(client: MCPClient, args: list[str]):
    if not args:
        print("  Usage: read <filename>\n")
        return
    name = args[0]
    content = client.read_document(name)
    print(f"\n  ── {name} {'─' * max(0, 44 - len(name))}")
    for line in content.splitlines():
        print(f"  {line}")
    print(f"  {'─' * 46}\n")


def cmd_edit(client: MCPClient, args: list[str]):
    if not args:
        print("  Usage: edit <filename>\n")
        return
    name = args[0]

    # Try to load existing content for preview
    try:
        existing = client.read_document(name)
    except Exception:
        existing = ""

    new_content = interactive_editor(existing)
    if new_content is None:
        return

    msg = client.edit_document(name, new_content)
    print(f"\n  ✅  {msg}\n")


def cmd_tools(client: MCPClient):
    tools = client.list_tools()
    print(f"\n  🔧  {len(tools)} tool(s) registered on the MCP server:\n")
    for t in tools:
        print(f"      • {t['name']}")
        print(f"        {t['description']}\n")


# ---------------------------------------------------------------------------
# Main REPL
# ---------------------------------------------------------------------------

def main():
    print(BANNER)

    client = MCPClient()
    try:
        client.start()
    except Exception as exc:
        print(f"  ❌  Failed to start MCP server: {exc}")
        sys.exit(1)

    print("  ✅  MCP server started.\n")

    try:
        while True:
            try:
                raw = input("chatbot> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n  Goodbye!")
                break

            if not raw:
                continue

            parts = raw.split()
            cmd, args = parts[0].lower(), parts[1:]

            if cmd in ("exit", "quit"):
                print("  Goodbye!")
                break
            elif cmd == "help":
                print(HELP_TEXT)
            elif cmd == "list":
                cmd_list(client)
            elif cmd == "read":
                cmd_read(client, args)
            elif cmd in ("edit", "new"):
                cmd_edit(client, args)
            elif cmd == "tools":
                cmd_tools(client)
            else:
                print(f"  Unknown command: '{cmd}'.  Type  help  for usage.\n")

    finally:
        client.stop()


if __name__ == "__main__":
    main()
