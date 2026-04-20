# CAMELOT_OS Universal MCP System

**Date:** 2026-03-04
**Version:** 1.0.0
**Architect:** Claude Opus 4.6
**Sovereign:** VaShawn O. Head

---

## 1. System Overview

This document defines the **Universal MCP System** — a unified layer that connects every AI tool in your development stack through the Model Context Protocol (MCP). Every tool sees the same servers, shares the same capabilities, and can be swapped or scaled independently.

```
┌─────────────────────────────────────────────────────────────────┐
│                    UNIVERSAL MCP BUS                            │
│                                                                 │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │  Ollama   │ │NotebookLM │ │Gemini CLI │ │ (Future)  │       │
│  │  14 tools │ │  30 tools │ │  4 tools  │ │ Firebase  │       │
│  │  Local LLM│ │  Research │ │  1M token │ │ Postgres  │       │
│  │  Embed    │ │  Audio/Vid│ │  Sandbox  │ │ Browser   │       │
│  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘       │
│        │              │             │              │            │
│        └──────────────┴──────┬──────┴──────────────┘            │
│                              │                                  │
│                         MCP Protocol                            │
│                       (stdio / HTTP)                            │
│                              │                                  │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐       │
│  │  Claude   │ │   Codex   │ │  Gemini   │ │   Goose   │       │
│  │   Code    │ │   CLI     │ │   CLI     │ │   CLI     │       │
│  └───────────┘ └───────────┘ └───────────┘ └───────────┘       │
│  ┌───────────┐ ┌───────────┐ ┌───────────┐                     │
│  │Antigravity│ │  OpenCode │ │  OpenMCP  │                     │
│  │   (IDE)   │ │   (CLI)   │ │  (GUI)    │                     │
│  └───────────┘ └───────────┘ └───────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

**Principle:** Any AI client can talk to any MCP server. Add a server once, every tool gains the capability. Swap a client, nothing else changes.

---

## 2. Complete Tool Inventory

### 2.1 AI Clients (Consumers)

| Tool | Type | Auth | Config Location | Status |
|---|---|---|---|---|
| **Claude Code** | CLI agent | Anthropic OAuth | `~/.claude.json` | Active |
| **OpenAI Codex** | CLI agent | ChatGPT OAuth | `~/.codex/config.toml` | Active (v0.107.0) |
| **Gemini CLI** | CLI agent | Google OAuth | `~/.gemini/settings.json` | Active (auto-gemini-3) |
| **Goose** | CLI agent | Configurable | `%APPDATA%/Block/goose/config/config.yaml` | Active (v1.23.2) |
| **Antigravity** | IDE (VS Code fork) | Google OAuth | `%APPDATA%/Antigravity/User/settings.json` | Active |
| **OpenCode** | CLI agent | Configurable | npm global | Installed (v1.1.26) |
| **OpenMCP** | GUI MCP client | N/A | `~/.openmcp/` | Installed (needs config) |

### 2.2 MCP Servers (Providers)

| Server | Package | Transport | Tools | Auth Required |
|---|---|---|---|---|
| **Ollama** | `ollama-mcp` (npm) | stdio | 14 tools | None (local) |
| **NotebookLM** | `notebooklm-mcp-cli` (uv) | stdio | 30 tools | Google OAuth via `nlm login` |
| **Gemini CLI Bridge** | `gemini-mcp-tool` (npm) | stdio | 4 tools | Uses installed Gemini CLI OAuth |

### 2.3 Local Model Servers

| Server | Type | Port | Models | Status |
|---|---|---|---|---|
| **Ollama** | Local LLM server | 11434 | Any GGUF model | Installing |
| **LM Studio** | Local LLM server | 1234 | Any GGUF model | Installed (empty) |

### 2.4 Auth Tokens (Current State)

| Service | Auth Method | Account |
|---|---|---|
| Anthropic (Claude) | OAuth subscription | vizion711@gmail.com (Pro) |
| OpenAI (Codex) | ChatGPT OAuth | vizion711@gmail.com (Plus) |
| Google (Gemini/Antigravity) | OAuth personal | vizion711@gmail.com |
| Google (NotebookLM) | Needs `nlm login` | Not yet authenticated |

---

## 3. Configuration Files (What Was Set Up)

### 3.1 Claude Code (`~/.claude.json` — user-level mcpServers)

```json
{
  "mcpServers": {
    "notebooklm-mcp": {
      "type": "stdio",
      "command": "notebooklm-mcp",
      "args": [],
      "env": {}
    },
    "gemini-cli": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "gemini-mcp-tool"],
      "env": {}
    },
    "ollama": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "ollama-mcp"],
      "env": {}
    }
  }
}
```

### 3.2 OpenAI Codex (`~/.codex/config.toml`)

```toml
[mcp_servers.ollama]
command = "npx"
args = ["-y", "ollama-mcp"]

[mcp_servers.ollama.env]
OLLAMA_HOST = "http://127.0.0.1:11434"

[mcp_servers.gemini-cli]
command = "npx"
args = ["-y", "gemini-mcp-tool"]

[mcp_servers.notebooklm]
command = "notebooklm-mcp"
args = ["run"]
```

### 3.3 Gemini CLI (`~/.gemini/settings.json`)

```json
{
  "mcpServers": {
    "ollama": {
      "command": "npx",
      "args": ["-y", "ollama-mcp"],
      "env": { "OLLAMA_HOST": "http://127.0.0.1:11434" }
    },
    "notebooklm": {
      "command": "notebooklm-mcp",
      "args": ["run"]
    }
  }
}
```

### 3.4 Goose (`%APPDATA%/Block/goose/config/config.yaml`)

```yaml
extensions:
  ollama:
    enabled: true
    type: stdio
    cmd: npx
    args: ["-y", "ollama-mcp"]
    env:
      OLLAMA_HOST: "http://127.0.0.1:11434"

  notebooklm:
    enabled: true
    type: stdio
    cmd: notebooklm-mcp
    args: ["run"]

  gemini-cli-mcp:
    enabled: true
    type: stdio
    cmd: npx
    args: ["-y", "gemini-mcp-tool"]
```

### 3.5 Antigravity + Gemini CLI (project-level `.gemini/settings.json`)

```json
{
  "mcpServers": {
    "ollama": {
      "command": "npx",
      "args": ["-y", "ollama-mcp"],
      "env": { "OLLAMA_HOST": "http://127.0.0.1:11434" }
    },
    "notebooklm": {
      "command": "notebooklm-mcp",
      "args": ["run"]
    }
  }
}
```

---

## 4. MCP Server Capabilities Matrix

### 4.1 Ollama MCP (14 tools)

| Tool | Function | Use Case |
|---|---|---|
| `ollama_list` | List installed models | Inventory check |
| `ollama_show` | Model details | Check params, license, size |
| `ollama_pull` | Download model | Get new models |
| `ollama_push` | Upload model | Share custom models |
| `ollama_copy` | Duplicate model | Create variants |
| `ollama_delete` | Remove model | Free disk space |
| `ollama_create` | Build from Modelfile | Custom model creation |
| `ollama_ps` | Running models | Monitor GPU/RAM usage |
| `ollama_generate` | Text completion | Fast local inference |
| `ollama_chat` | Interactive chat | Multi-turn local conversations |
| `ollama_embed` | Generate embeddings | Vector search, RAG, similarity |
| `ollama_web_search` | Web search | Research (cloud feature) |
| `ollama_web_fetch` | Fetch URL content | Content extraction |
| `ollama_version` | Server version | Diagnostics |

### 4.2 NotebookLM MCP (30 tools)

| Category | Tools | Function |
|---|---|---|
| Notebook Mgmt | `notebook_list`, `notebook_create`, `notebook_query` | CRUD + AI chat with notebook |
| Sources | `source_add`, `source_sync_drive` | Add URLs, files, Drive docs |
| Studio | `studio_create`, `studio_revise` | Generate audio, video, infographics, summaries |
| Download | `download_artifact` | Retrieve generated content |
| Sharing | `notebook_share_public`, `notebook_share_invite` | Collaboration |
| Research | `research_start` | Autonomous web/Drive research |

### 4.3 Gemini CLI Bridge (4 tools)

| Tool | Function | Use Case |
|---|---|---|
| `ask-gemini` | Query Gemini with 1M token window | Large file analysis, codebase understanding |
| `sandbox-test` | Execute code in Gemini sandbox | Safe testing without local side effects |
| `Ping` | Test connection | Diagnostics |
| `Help` | Show help | Reference |

---

## 5. Scaling Guide

### 5.1 Adding a New MCP Server

To add a new MCP server to the entire system, update these files:

**1. Claude Code:**
```bash
claude mcp add <name> -s user -- <command> [args...]
```

**2. Codex:** Add to `~/.codex/config.toml`:
```toml
[mcp_servers.<name>]
command = "<command>"
args = ["<args>"]
```

**3. Gemini CLI:** Add to `~/.gemini/settings.json` under `mcpServers`:
```json
"<name>": { "command": "<cmd>", "args": ["<args>"] }
```

**4. Goose:** Add to `%APPDATA%/Block/goose/config/config.yaml` under `extensions`:
```yaml
<name>:
  enabled: true
  type: stdio
  cmd: <command>
  args: ["<args>"]
```

**5. Antigravity/Gemini project-level:** Add to `.gemini/settings.json` in project root.

### 5.2 Recommended Future MCP Servers

| Server | Package | What It Adds | Priority |
|---|---|---|---|
| **Firebase** | `npx -y firebase-tools@latest mcp` | Firestore, Auth, Hosting, Crashlytics | HIGH |
| **GitHub** | `npx -y @github/mcp-server` | Issues, PRs, repos, code search | HIGH |
| **Filesystem** | `npx -y @anthropic/mcp-filesystem` | Scoped file access for agents | MEDIUM |
| **PostgreSQL** | `npx -y @anthropic/mcp-postgres` | Direct DB queries | MEDIUM |
| **Brave Search** | `npx -y @anthropic/mcp-brave-search` | Web search without API vendor lock | MEDIUM |
| **Puppeteer** | `npx -y @anthropic/mcp-puppeteer` | Browser automation, screenshots | LOW |
| **Memory** | `npx -y @anthropic/mcp-memory` | Persistent knowledge graph | LOW |
| **Docker** | `npx -y @docker/mcp-server` | Container management | LOW |
| **Context7** | `npx -y @upstash/context7-mcp` | Up-to-date library docs | LOW |

To add any of these:
```bash
# Example: Add GitHub MCP to all tools at once
claude mcp add github -s user -- npx -y @github/mcp-server
# Then manually add same entry to codex/gemini/goose configs
```

### 5.3 Adding OpenAI-Compatible Servers

Any server that exposes an OpenAI-compatible API (LocalAI, LM Studio, vLLM, text-generation-webui) can be used via Ollama's MCP or directly:

**LocalAI as MCP backend:**
```bash
# Start LocalAI
docker run -p 8080:8080 localai/localai

# Point Ollama MCP at it (they share compatible APIs)
# Or use a dedicated OpenAI-compat MCP:
claude mcp add localai -s user -e OPENAI_BASE_URL=http://localhost:8080/v1 -- npx -y openai-mcp-server
```

**LM Studio:**
```bash
# LM Studio runs on port 1234 with OpenAI-compat API
# Start it from LM Studio GUI, then:
claude mcp add lmstudio -s user -e OPENAI_BASE_URL=http://localhost:1234/v1 -- npx -y openai-mcp-server
```

**Any OpenAI-compatible endpoint:**
```bash
claude mcp add <name> -s user \
  -e OPENAI_BASE_URL=http://localhost:<port>/v1 \
  -e OPENAI_API_KEY=<key-or-dummy> \
  -- npx -y openai-mcp-server
```

### 5.4 Scaling Ollama Models

After Ollama is installed, pull models for different use cases:

```bash
# Small & fast (intent classification, quick tasks)
ollama pull qwen3:0.6b           # 400MB, runs on anything
ollama pull phi3:mini             # 2.2GB, great balance

# Medium (coding, analysis)
ollama pull qwen3:8b              # 8GB, strong coder
ollama pull codellama:7b          # 7GB, code specialist

# Large (reasoning, complex tasks)
ollama pull qwen3-coder:30b       # 30GB, needs 32GB+ RAM
ollama pull llama3.1:70b          # Needs GPU with 48GB+ VRAM

# Embedding models (for RAG/search)
ollama pull nomic-embed-text      # 274MB, excellent embeddings
ollama pull mxbai-embed-large     # 670MB, highest quality
```

Every model you pull is instantly available to ALL clients via the Ollama MCP server. No per-tool configuration needed.

---

## 6. How Each Tool Uses the System

### 6.1 Claude Code (Primary Workstation)

Claude Code is the orchestrator. With all three MCP servers:

```
You: "Analyze my CAMELOT_OS codebase and create a NotebookLM research notebook"

Claude Code:
  1. Uses Gemini CLI MCP → ask-gemini with @src/ files (1M token window)
  2. Gets structural analysis back
  3. Uses NotebookLM MCP → notebook_create "CAMELOT Architecture Analysis"
  4. Uses NotebookLM MCP → source_add with key files
  5. Uses NotebookLM MCP → studio_create audio summary
  6. Returns: "Created notebook with audio overview. Here's the analysis..."
```

### 6.2 OpenAI Codex (Code Specialist)

Codex focuses on code generation with access to local models:

```
codex "refactor this module to use dependency injection"
  → Codex uses its own o3/o4-mini for reasoning
  → Can delegate to Ollama MCP for local model comparison
  → Can use Gemini CLI MCP for sandbox testing
```

### 6.3 Gemini CLI (Research & Analysis)

Gemini has the largest context window (1M tokens) + Google Search:

```
gemini "analyze the security audit report and cross-reference with OWASP top 10"
  → Uses native Gemini 3 with grounded search
  → Can access Ollama for local embedding comparison
  → Can push results to NotebookLM for persistence
```

### 6.4 Goose (Autonomous Agent)

Goose runs autonomous multi-step tasks with all extensions:

```
goose "set up a CI pipeline that tests on all platforms"
  → Uses its agent loop to plan → execute → verify
  → Can use Ollama for local model-assisted code review
  → Can use Gemini CLI for large file analysis
  → Can use NotebookLM for documenting decisions
```

### 6.5 Antigravity (Visual IDE)

Antigravity shares MCP servers via `.gemini/settings.json`:

```
Agent Manager → "Build a React dashboard for CAMELOT_OS"
  → Antigravity agents plan and write code
  → Ollama MCP available for local model queries
  → NotebookLM available for research context
  → Shares project files with Claude Code / Gemini CLI
```

---

## 7. Architecture Principles

### 7.1 Server Independence

Each MCP server is stateless and independently replaceable:
- Swap Ollama for LocalAI → change one line in each config
- Swap NotebookLM for a different research tool → update server entry
- Add 10 more servers → each tool gains 10x more capabilities

### 7.2 Auth Isolation

Each service handles its own auth:
- Ollama: No auth (localhost only)
- NotebookLM: Google OAuth via `nlm login`
- Gemini CLI: Google OAuth via `gemini` CLI
- Codex: OpenAI ChatGPT OAuth
- Claude: Anthropic OAuth

No service can access another service's credentials. The MCP protocol doesn't pass auth tokens between servers.

### 7.3 Local-First

The system works without internet for:
- Ollama (fully local LLM inference)
- File operations (native to each client)
- Code execution (local sandboxes)

Internet required only for:
- NotebookLM (Google cloud service)
- Gemini CLI bridge (calls Gemini API)
- Ollama cloud features (web search/fetch)

### 7.4 Cost Optimization

| Task Type | Best Client | Cost |
|---|---|---|
| Quick local inference | Ollama MCP via any client | Free (your hardware) |
| Large file analysis | Gemini CLI (1M tokens) | Free tier (60 req/min) |
| Complex reasoning | Claude Code (Opus 4.6) | Anthropic subscription |
| Code generation | Codex (o3/o4-mini) | OpenAI Plus subscription |
| Research & summaries | NotebookLM | Free (Google account) |
| Autonomous tasks | Goose (any LLM backend) | Depends on chosen model |

---

## 8. Remaining Setup Steps

### Immediate (Do Now)

- [ ] **Complete Ollama installation** — finish the setup wizard
- [ ] **Pull a starter model**: `ollama pull qwen3:8b`
- [ ] **Authenticate NotebookLM**:
  ```powershell
  $env:PYTHONIOENCODING="utf-8"
  nlm login
  ```
- [ ] **Add Goose to PATH**: Add `C:\Users\vizio\goose` to your system PATH
- [ ] **Restart Claude Code** to activate all MCP servers

### Verify Everything Works

After restart, in Claude Code:
```
/mcp                          # Should show: ollama, gemini-cli, notebooklm-mcp
```

In Codex:
```
codex mcp list                # Should show: ollama, gemini-cli, notebooklm
```

In Gemini CLI:
```
gemini                        # Start session
/mcp                          # Should show: ollama, notebooklm
```

In Goose:
```
C:\Users\vizio\goose\goose.exe session
# Extensions should list: Ollama, NotebookLM, Gemini CLI
```

### Optional Enhancements

- [ ] Add GitHub MCP: `claude mcp add github -s user -- npx -y @github/mcp-server`
- [ ] Add Firebase MCP: `claude mcp add firebase -s user -- npx -y firebase-tools@latest mcp`
- [ ] Configure LM Studio as OpenAI-compat endpoint
- [ ] Install LocalAI for multi-modal inference (STT/TTS/Vision)

---

## 9. Troubleshooting

### Ollama MCP Can't Connect
```bash
# Verify Ollama is running
curl http://127.0.0.1:11434/api/tags

# If not running, start it
ollama serve

# Check models available
ollama list
```

### NotebookLM Auth Fails
```bash
# Re-authenticate
$env:PYTHONIOENCODING="utf-8"
nlm login

# Check status
nlm login --check

# Diagnose issues
nlm doctor
```

### Gemini CLI Bridge Not Working
```bash
# Verify Gemini CLI works independently
gemini -p "hello"

# If OAuth expired, re-auth
gemini auth login
```

### MCP Server Crashes
```bash
# Test server independently
npx -y ollama-mcp              # Should start without errors
npx -y gemini-mcp-tool         # Should start without errors
notebooklm-mcp run             # Should start without errors

# Check npm cache issues
npm cache clean --force
```

### Adding Custom OpenAI-Compatible Server
```bash
# Template for any OpenAI-compatible endpoint
claude mcp add <name> -s user \
  -e OPENAI_BASE_URL=http://<host>:<port>/v1 \
  -e OPENAI_API_KEY=<key> \
  -- npx -y openai-mcp-server

# Examples:
# LocalAI:    OPENAI_BASE_URL=http://localhost:8080/v1
# LM Studio:  OPENAI_BASE_URL=http://localhost:1234/v1
# vLLM:       OPENAI_BASE_URL=http://localhost:8000/v1
# text-gen:   OPENAI_BASE_URL=http://localhost:5000/v1/
# Groq:       OPENAI_BASE_URL=https://api.groq.com/openai/v1
# Together:   OPENAI_BASE_URL=https://api.together.xyz/v1
# Fireworks:  OPENAI_BASE_URL=https://api.fireworks.ai/inference/v1
```

---

## 10. File Reference

| File | Tool | What It Configures |
|---|---|---|
| `~/.claude.json` | Claude Code | MCP servers (user-level) |
| `~/.codex/config.toml` | OpenAI Codex | MCP servers + project trust |
| `~/.gemini/settings.json` | Gemini CLI | MCP servers + auth + model |
| `%APPDATA%/Block/goose/config/config.yaml` | Goose | Extensions (MCP servers) |
| `%APPDATA%/Antigravity/User/settings.json` | Antigravity | Editor settings |
| `.gemini/settings.json` (project) | Gemini CLI + Antigravity | Project-level MCP servers |
| `~/.openmcp/connection.json` | OpenMCP | Server connections (empty) |
| `~/.codex/auth.json` | Codex | OpenAI ChatGPT OAuth tokens |

---

*This system is designed to scale. Add servers, swap clients, pull models — the MCP bus handles the routing. Every tool in your stack speaks the same protocol.*
