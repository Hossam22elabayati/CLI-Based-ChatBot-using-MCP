# 📄 Document Chatbot — MCP Intro Project

A **CLI chatbot** that lets you manage a collection of plain-text documents using the
**Model Context Protocol (MCP)** — the open standard that lets AI models talk to external tools.

This project is a hands-on introduction to MCP: you will see a real **MCP server** and
**MCP client** talking to each other over stdio, with two tools exposed to the user.

---

## 📁 Project Structure

```
mcp/
├── main.py              ← Entry point — CLI chatbot (REPL loop)
├── mcp_server.py        ← MCP server (exposes tools via the mcp SDK)
├── mcp_client.py        ← MCP client (connects to server, calls tools)
├── core/
│   ├── __init__.py
│   └── documents.py     ← File I/O logic (reads/writes ./documents/)
├── documents/           ← Your document collection lives here
│   ├── sample.txt
│   └── about-mcp.txt
├── pyproject.toml       ← Project dependencies (uv / pip)
└── README.md
```

---

## 🏗️ How It Works

```
You (terminal)
      │
      ▼
  main.py  ←─── CLI chatbot, reads your commands
      │
      ▼
mcp_client.py  ──── JSON-RPC 2.0 over stdin/stdout ────►  mcp_server.py
                          (MCP protocol)                         │
                                                                 ▼
                                                         core/documents.py
                                                         reads/writes ./documents/
```

The **MCP server** exposes two tools:

| Tool | What it does |
|------|-------------|
| `read_document` | Read any file from `./documents/` |
| `edit_document` | Create or overwrite a file in `./documents/` |

The **MCP client** launches the server as a subprocess and communicates using the
official `mcp` Python SDK — exactly the same way Claude Desktop talks to MCP servers.

---

## ⚙️ Requirements

| Requirement | Version |
|-------------|---------|
| Python | **3.10 or newer** |
| uv | any recent version |

> ✅ Tested on Python 3.11 / RHEL 9

---

## 🚀 Installation & Running

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
```

### 2. Pin Python version (if you have multiple versions)

```bash
uv python pin 3.11
```

> Skip this step if `python --version` already shows 3.10+.

### 3. Install dependencies

```bash
uv add mcp anthropic
```

This creates a `.venv/` virtual environment and installs all required packages automatically.

### 4. Run the chatbot

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
  ── sample.txt ──────────────────────────────────
  This is a sample document. Edit me with the edit command.
  ────────────────────────────────────────────────

chatbot> new meeting-notes.txt
  ┌─ Editor ──────────────────────────────────────────┐
  │  Type your content. Enter  !save  on a blank line │
  │  to save, or Ctrl-C to cancel.                    │
  └────────────────────────────────────────────────────┘
  | Team standup - 2025-05-14
  | - Reviewed MCP project
  | - Next: connect a real LLM
  | !save
  ✅  Document 'meeting-notes.txt' saved successfully.

chatbot> tools
  🔧  2 tool(s) registered on the MCP server:

      • read_document
        Read the full text content of a document from the collection.

      • edit_document
        Create or overwrite a document in the collection.

chatbot> exit
  Goodbye!
```

---

## 🔑 Key MCP Concepts Demonstrated

| Concept | Where |
|---------|-------|
| `initialize` / `initialized` handshake | `mcp_client.py` → `start()` |
| `tools/list` — server advertises capabilities | `mcp_server.py` → `handle_list_tools()` |
| `tools/call` — client invokes a tool | `mcp_client.py` → `read_document()` / `edit_document()` |
| `resources/list` — server exposes document collection | `mcp_server.py` → `handle_list_resources()` |
| stdio transport | `mcp_server.py` → `stdio_server()` |

---

## 🔧 Troubleshooting

**`error: Requirement name 'mcp' matches project name`**
```bash
sed -i 's/name = "mcp"/name = "doc-chatbot"/' pyproject.toml
uv add mcp anthropic
```

**`mcp requires Python >=3.10`**
```bash
uv python pin 3.11
sed -i 's/>=3.9/>=3.10/' pyproject.toml
uv add mcp anthropic
```

**`No pyproject.toml found`**
```bash
uv init --no-readme
# then follow the steps above
```

---

## 💡 Ideas to Extend the Project

- **`delete_document` tool** — add it in `mcp_server.py` and `core/documents.py`
- **`search_documents` tool** — search text across all documents
- **Connect a real LLM** — pass the tool definitions to Claude or OpenAI and let the model decide which tool to call
- **Multiple servers** — add a second MCP server for a contacts list or task manager

---

## 📚 Resources

- [MCP Official Docs](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Anthropic Claude API](https://docs.anthropic.com)
- [uv — Python package manager](https://docs.astral.sh/uv)
