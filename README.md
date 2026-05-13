# 📄 Document Chatbot — MCP Intro Project

A **CLI chatbot** that manages a collection of plain-text documents using the
**Model Context Protocol (MCP)** — the open standard for connecting AI models to external tools.

This project is a hands-on introduction to MCP. It shows a real **MCP server** and
**MCP client** talking to each other over stdio, with three tools exposed to the user.

---

## 📁 Project Structure

```
mcp/
├── main.py              ← Entry point — CLI chatbot (REPL loop)
├── mcp_server.py        ← MCP server built with FastMCP
├── mcp_client.py        ← MCP client — connects to server and calls tools
├── core/
│   ├── __init__.py
│   └── documents.py     ← File I/O logic (reads/writes ./documents/)
├── documents/           ← Your document collection (created automatically)
│   ├── sample.txt
│   └── about-mcp.txt
├── pyproject.toml       ← Project metadata and dependencies
├── .gitignore
└── README.md
```

---

## 🏗️ How It Works

```
You (terminal)
      │
      ▼
  main.py          ← reads your commands
      │
      ▼
mcp_client.py  ──── MCP protocol (stdio) ────►  mcp_server.py  (FastMCP)
                                                       │
                                                       ▼
                                               core/documents.py
                                               reads/writes ./documents/
```

The **MCP server** exposes three tools:

| Tool | What it does |
|------|-------------|
| `read_document_tool` | Read any file from `./documents/` |
| `edit_document_tool` | Create or overwrite a file |
| `list_documents_tool` | List all files in the collection |

---

## ⚙️ Requirements

| Requirement | Version |
|-------------|---------|
| Python | **3.10 or newer** (3.11 recommended) |
| uv | any recent version |
| Node.js + npm | only needed for `mcp dev` inspector UI |

> ✅ Tested on Python 3.11 / RHEL 9

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Check your Python version

```bash
python3 --version
```

If you have multiple versions (e.g. 3.9 and 3.11), pin to 3.11:

```bash
uv python pin 3.11
```

### 3. Install dependencies

```bash
uv add "mcp[cli]" anthropic
```

This creates `.venv/` and installs all required packages automatically.

> **Troubleshooting — project name conflict:**
> If you see `Requirement name 'mcp' matches project name`, run:
> ```bash
> sed -i 's/name = "mcp"/name = "doc-chatbot"/' pyproject.toml
> uv add "mcp[cli]" anthropic
> ```

> **Troubleshooting — Python version too old:**
> If you see `mcp requires Python >=3.10`, run:
> ```bash
> uv python pin 3.11
> sed -i 's/>=3.9/>=3.10/' pyproject.toml
> uv add "mcp[cli]" anthropic
> ```

---

## ▶️ Running the Chatbot

```bash
uv run python main.py
```

You should see:

```
╔══════════════════════════════════════════════╗
║         📄  Document Chatbot (MCP)           ║
║  Type  help  to see available commands.      ║
╚══════════════════════════════════════════════╝

  ✅  MCP server started.

chatbot>
```

---

## 💬 Chatbot Commands

| Command | Description |
|---------|-------------|
| `list` | Show all documents in the collection |
| `read <filename>` | Print the content of a document |
| `edit <filename>` | Open interactive editor to update a document |
| `new <filename>` | Create a new document (alias for `edit`) |
| `tools` | Show the MCP tools the server exposes |
| `help` | Show the help message |
| `exit` | Quit the chatbot |

---

## 🧪 Example Session

```
chatbot> list
  📁  2 document(s):
      • about-mcp.txt
      • sample.txt

chatbot> read sample.txt
  ── sample.txt ─────────────────────────────────────
  This is a sample document. Edit me with the edit command.
  ───────────────────────────────────────────────────

chatbot> new meeting-notes.txt
  ┌─ Editor ──────────────────────────────────────────┐
  │  Type your content. Enter  !save  on a blank line │
  │  to save, or Ctrl-C to cancel.                    │
  └────────────────────────────────────────────────────┘
  | Team standup - 2025-05-14
  | - Reviewed MCP project
  | !save
  ✅  Document 'meeting-notes.txt' saved successfully.

chatbot> tools
  🔧  3 tool(s) registered on the MCP server:
      • read_document_tool
      • edit_document_tool
      • list_documents_tool

chatbot> exit
  Goodbye!
```

---

## 🔍 MCP Inspector (Browser UI)

The MCP Inspector lets you test your tools visually in a browser — no chatbot needed.

### Requirements

Install Node.js first (needed by the inspector):

```bash
# RHEL / CentOS
dnf install -y nodejs

# Ubuntu / Debian
apt install -y nodejs npm
```

### Run the inspector

```bash
uv run mcp dev mcp_server.py
```

This opens a browser UI where you can:
- See all tools and their input schemas
- Call any tool manually and see the response
- Debug your server without writing any client code

---

## 🔑 Key MCP Concepts Demonstrated

| Concept | Where in code |
|---------|--------------|
| FastMCP server setup | `mcp_server.py` — `mcp = FastMCP("doc-server")` |
| Tool definition with decorator | `mcp_server.py` — `@mcp.tool()` |
| Resource definition | `mcp_server.py` — `@mcp.resource("doc://{name}")` |
| MCP handshake | `mcp_client.py` — `session.initialize()` |
| Tool call from client | `mcp_client.py` — `session.call_tool(...)` |
| stdio transport | `mcp_client.py` — `stdio_client(server_params)` |

---

## 📦 Dependencies Explained

| Package | Why |
|---------|-----|
| `mcp[cli]` | MCP Python SDK + `mcp dev` inspector command |
| `anthropic` | Anthropic API client (for future LLM integration) |

All managed by **uv** — a fast Python package manager.
`uv add <package>` installs and saves to `pyproject.toml` automatically.

---

## 💡 Ideas to Extend the Project

- **`delete_document` tool** — add `@mcp.tool()` in `mcp_server.py` + delete logic in `core/documents.py`
- **`search_documents` tool** — search text across all documents
- **Connect Claude** — pass tool definitions to the Anthropic API and let Claude decide which tool to call based on user input
- **Second MCP server** — add a contacts list or task manager as a separate server

---

## 📚 Resources

- [MCP Official Docs](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Guide](https://github.com/modelcontextprotocol/python-sdk#fastmcp)
- [uv Documentation](https://docs.astral.sh/uv)
- [Anthropic API Docs](https://docs.anthropic.com)
