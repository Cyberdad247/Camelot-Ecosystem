"""Camelot Chat -- Multi-turn terminal chat interface.

Standalone REPL that maintains conversation history and routes through
llm_router (all 8 providers + fallback chain). Invoked directly via
`py chat.py` or from the HUD via the `//CHAT` rune.

Slash commands:
    /help                 show commands
    /model <name>         set model (e.g. /model claude-opus-4-6)
    /provider <name>      pin provider (e.g. /provider cliproxy); "auto" clears
    /system <text>        replace system prompt
    /clear                reset history (keeps system prompt)
    /history              show message count + last turn
    /save [name]          save transcript to chat_sessions/<name>.json
    /load <name>          load transcript
    /providers            list available providers
    /exit | /quit         leave chat
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.markdown import Markdown

sys.path.insert(0, str(Path(__file__).resolve().parent))
from llm_router import chat as llm_chat, list_available

console = Console()

CAMELOT_HOME = Path(os.environ.get("CAMELOT_OS_HOME") or Path(__file__).resolve().parents[3])
SESSIONS_DIR = Path(__file__).resolve().parent / "chat_sessions"
PROTOCOLS_MD = CAMELOT_HOME / "docs" / "reference" / "PROTOCOLS.md"
COMMANDS_MD = CAMELOT_HOME / "docs" / "reference" / "COMMANDS.md"
KNIGHTS_MD = CAMELOT_HOME / "03_VAULT" / "Knights" / "README.md"
CARTRIDGES_DIR = Path(__file__).resolve().parent / "cartridges"
DEFAULT_SYSTEM = (
    "You are the Camelot OS conversational assistant. Be concise, direct, "
    "and format code blocks with language hints. Favor markdown."
)

HELP = """[bold bright_yellow]Camelot Chat — Commands[/]
  [cyan]/help[/]              this list
  [cyan]/model <name>[/]      set model override
  [cyan]/provider <name>[/]   pin provider (auto to clear)
  [cyan]/system <text>[/]     replace system prompt
  [cyan]/clear[/]             reset conversation
  [cyan]/history[/]           show turn count + loaded assets
  [cyan]/save [name][/]       save to chat_sessions/
  [cyan]/load <name>[/]       load transcript
  [cyan]/providers[/]         list provider status

[bold bright_yellow]Asset Loaders[/] [dim](inject into system prompt)[/]
  [cyan]/protocols[/]                list protocol sections
  [cyan]/protocol <name>[/]          load protocol section
  [cyan]/commands[/]                 list command sections
  [cyan]/command <name>[/]           load command section
  [cyan]/roster[/] | [cyan]/knights[/]        list knight orders
  [cyan]/knight <name>[/]            load knight order/persona
  [cyan]/cartridges[/]               list cartridges
  [cyan]/cartridge <name>[/]         load cartridge (YAML)
  [cyan]/unload[/]                   drop all loaded assets

  [cyan]/exit[/]              leave chat
"""


# ── Asset loaders ─────────────────────────────────────────────────────

_HEADING_RE = re.compile(r"^(#{2,4})\s+(.+?)\s*$")


def _parse_md_sections(path: Path) -> dict[str, str]:
    """Parse a markdown doc into {heading_slug: body} keyed by ## and ### headings."""
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    sections: dict[str, str] = {}
    current_key: str | None = None
    current_body: list[str] = []
    for line in lines:
        m = _HEADING_RE.match(line)
        if m:
            if current_key is not None:
                sections[current_key] = "\n".join(current_body).strip()
            title = m.group(2).strip()
            current_key = _slug(title)
            current_body = [f"## {title}"]
        else:
            current_body.append(line)
    if current_key is not None:
        sections[current_key] = "\n".join(current_body).strip()
    return sections


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def _fuzzy_pick(query: str, keys: list[str]) -> str | None:
    q = _slug(query)
    if q in keys:
        return q
    matches = [k for k in keys if q in k]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        return matches[0]  # first match wins
    return None


def _list_cartridges() -> list[str]:
    if not CARTRIDGES_DIR.exists():
        return []
    return sorted(p.stem for p in CARTRIDGES_DIR.glob("*.yaml"))


def _load_cartridge(name: str) -> tuple[str, str] | None:
    cart = CARTRIDGES_DIR / f"{name}.yaml"
    if not cart.exists():
        cart = CARTRIDGES_DIR / f"{_slug(name)}.yaml"
    if not cart.exists():
        avail = _list_cartridges()
        match = _fuzzy_pick(name, avail)
        if match:
            cart = CARTRIDGES_DIR / f"{match}.yaml"
        else:
            return None
    return cart.stem, cart.read_text(encoding="utf-8", errors="replace")


def _inject(session: "ChatSession", label: str, body: str):
    block = f"\n\n<!-- loaded: {label} -->\n{body}\n<!-- /loaded: {label} -->"
    session.system = session.system + block
    session.loaded.append(label)
    console.print(f"[green]loaded[/] [cyan]{label}[/] [dim]({len(body)} chars)[/]")


def _handle_asset_list(kind: str):
    if kind == "protocols":
        keys = list(_parse_md_sections(PROTOCOLS_MD).keys())
    elif kind == "commands":
        keys = list(_parse_md_sections(COMMANDS_MD).keys())
    elif kind == "roster":
        keys = list(_parse_md_sections(KNIGHTS_MD).keys())
    elif kind == "cartridges":
        keys = _list_cartridges()
    else:
        keys = []
    if not keys:
        console.print(f"[yellow]no {kind} found[/]")
        return
    console.print(f"[bold]{kind} ({len(keys)})[/]")
    for k in keys:
        console.print(f"  [cyan]{k}[/]")


def _handle_asset_load(session: "ChatSession", kind: str, name: str):
    if not name:
        console.print(f"[red]usage: /{kind} <name>[/]")
        return
    if kind == "cartridge":
        result = _load_cartridge(name)
        if not result:
            console.print(f"[red]cartridge not found: {name}[/] (try /cartridges)")
            return
        stem, body = result
        _inject(session, f"cartridge:{stem}", body)
        return

    path_map = {"protocol": PROTOCOLS_MD, "command": COMMANDS_MD, "knight": KNIGHTS_MD}
    path = path_map[kind]
    sections = _parse_md_sections(path)
    if not sections:
        console.print(f"[red]source missing: {path}[/]")
        return
    pick = _fuzzy_pick(name, list(sections.keys()))
    if not pick:
        console.print(f"[red]{kind} not found: {name}[/] (try /{kind}s)")
        return
    _inject(session, f"{kind}:{pick}", sections[pick])


class ChatSession:
    def __init__(self, system: str = DEFAULT_SYSTEM):
        self.system = system
        self.turns: list[dict] = []
        self.provider: str | None = None
        self.model: str | None = None
        self.loaded: list[str] = []

    def messages(self) -> list[dict]:
        msgs = [{"role": "system", "content": self.system}]
        msgs.extend(self.turns)
        return msgs

    def add_user(self, text: str):
        self.turns.append({"role": "user", "content": text})

    def add_assistant(self, text: str):
        self.turns.append({"role": "assistant", "content": text})

    def clear(self):
        self.turns = []

    def to_dict(self) -> dict:
        return {
            "system": self.system,
            "provider": self.provider,
            "model": self.model,
            "turns": self.turns,
            "loaded": self.loaded,
            "saved_at": datetime.now().isoformat(timespec="seconds"),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ChatSession":
        s = cls(system=data.get("system", DEFAULT_SYSTEM))
        s.provider = data.get("provider")
        s.model = data.get("model")
        s.turns = data.get("turns", [])
        s.loaded = data.get("loaded", [])
        return s


def _save(session: ChatSession, name: str | None) -> Path:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    if not name:
        name = datetime.now().strftime("chat_%Y%m%d_%H%M%S")
    if not name.endswith(".json"):
        name += ".json"
    path = SESSIONS_DIR / name
    path.write_text(json.dumps(session.to_dict(), indent=2), encoding="utf-8")
    return path


def _load(name: str) -> ChatSession:
    if not name.endswith(".json"):
        name += ".json"
    path = SESSIONS_DIR / name
    data = json.loads(path.read_text(encoding="utf-8"))
    return ChatSession.from_dict(data)


def _handle_slash(session: ChatSession, line: str) -> bool:
    """Return True if chat should continue, False to exit."""
    parts = line.strip().split(maxsplit=1)
    cmd = parts[0].lower()
    arg = parts[1] if len(parts) > 1 else ""

    if cmd in ("/exit", "/quit", "/q"):
        console.print("[dim]Leaving chat.[/]")
        return False
    if cmd == "/help":
        console.print(HELP)
    elif cmd == "/model":
        session.model = arg or None
        console.print(f"[green]model = {session.model or '(default)'}[/]")
    elif cmd == "/provider":
        session.provider = None if arg.lower() in ("", "auto", "none") else arg
        console.print(f"[green]provider = {session.provider or 'auto (fallback chain)'}[/]")
    elif cmd == "/system":
        if arg:
            session.system = arg
            console.print("[green]system prompt updated[/]")
        else:
            console.print(Panel(session.system, title="system", border_style="dim"))
    elif cmd == "/clear":
        session.clear()
        console.print("[green]history cleared[/]")
    elif cmd == "/history":
        console.print(f"[cyan]{len(session.turns)} turns[/] | provider={session.provider or 'auto'} model={session.model or '(default)'}")
        if session.loaded:
            console.print(f"[dim]loaded assets:[/] {', '.join(session.loaded)}")
        if session.turns:
            last = session.turns[-1]
            preview = last["content"][:200]
            console.print(f"[dim]last[{last['role']}]:[/] {preview}")
    elif cmd == "/unload":
        session.system = re.sub(
            r"\n\n<!-- loaded: [^>]+ -->.*?<!-- /loaded: [^>]+ -->",
            "",
            session.system,
            flags=re.DOTALL,
        )
        session.loaded = []
        console.print("[green]all loaded assets dropped[/]")
    elif cmd in ("/protocols", "/commands", "/cartridges"):
        _handle_asset_list(cmd[1:])
    elif cmd in ("/roster", "/knights"):
        _handle_asset_list("roster")
    elif cmd == "/protocol":
        _handle_asset_load(session, "protocol", arg)
    elif cmd == "/command":
        _handle_asset_load(session, "command", arg)
    elif cmd == "/knight":
        _handle_asset_load(session, "knight", arg)
    elif cmd == "/cartridge":
        _handle_asset_load(session, "cartridge", arg)
    elif cmd == "/save":
        path = _save(session, arg or None)
        console.print(f"[green]saved ->[/] {path}")
    elif cmd == "/load":
        if not arg:
            console.print("[red]usage: /load <name>[/]")
        else:
            try:
                loaded = _load(arg)
                session.system = loaded.system
                session.turns = loaded.turns
                session.provider = loaded.provider
                session.model = loaded.model
                console.print(f"[green]loaded {len(session.turns)} turns[/]")
            except FileNotFoundError:
                console.print(f"[red]not found: {arg}[/]")
    elif cmd == "/providers":
        for p in list_available():
            console.print(f"  [cyan]{p['name']:<12}[/] {p['status']:<25} [dim]{p['default_model']}[/]")
    else:
        console.print(f"[red]unknown command: {cmd}[/] — try /help")
    return True


def _send(session: ChatSession, user_text: str):
    session.add_user(user_text)
    start = time.time()
    with console.status("[dim]thinking…[/]", spinner="dots"):
        result = llm_chat(
            session.messages(),
            provider=session.provider,
            model=session.model,
        )
    elapsed = int((time.time() - start) * 1000)

    if result.get("error"):
        session.turns.pop()  # drop the user turn on hard failure
        console.print(f"[red]error:[/] {result['error']}")
        return

    content = result.get("content", "")
    session.add_assistant(content)

    prov = result.get("provider", "?")
    model = result.get("model", "?")
    tokens = result.get("usage", {}).get("completion_tokens", "?")
    header = f"[bold bright_blue]{prov}[/]/{model} [dim]({elapsed}ms, {tokens} tok)[/]"
    console.print()
    console.print(header)
    try:
        body = Markdown(content) if content.strip() else "[dim](empty)[/]"
    except Exception:
        body = content
    console.print(Panel(body, border_style="bright_blue", padding=(1, 2)))


def run_chat(system: str | None = None, provider: str | None = None,
             model: str | None = None):
    """Launch the interactive chat REPL."""
    session = ChatSession(system=system or DEFAULT_SYSTEM)
    session.provider = provider
    session.model = model

    console.print(Panel(
        "[bold bright_magenta]Camelot Chat[/] — multi-turn REPL\n"
        "[dim]/help for commands · /exit to leave · blank line cancels[/]",
        border_style="bright_magenta",
    ))

    while True:
        try:
            console.print()
            line = Prompt.ask("[bold bright_green]you[/]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]leaving chat.[/]")
            return

        if not line:
            continue
        if line.startswith("/"):
            if not _handle_slash(session, line):
                return
            continue

        _send(session, line)


def main():
    import argparse
    ap = argparse.ArgumentParser(prog="chat", description="Camelot terminal chat")
    ap.add_argument("--provider", "-p", help="pin a provider (e.g. cliproxy, claude, ollama)")
    ap.add_argument("--model", "-m", help="model override")
    ap.add_argument("--system", "-s", help="system prompt override")
    ap.add_argument("--load", "-l", help="load a saved session by name")
    args = ap.parse_args()

    os.environ.setdefault("PYTHONIOENCODING", "utf-8")

    if args.load:
        session = _load(args.load)
        console.print(f"[green]loaded {len(session.turns)} turns from {args.load}[/]")
        if args.provider:
            session.provider = args.provider
        if args.model:
            session.model = args.model
        console.print(Panel(
            "[bold bright_magenta]Camelot Chat[/] — resumed\n[dim]/help · /exit[/]",
            border_style="bright_magenta",
        ))
        while True:
            try:
                console.print()
                line = Prompt.ask("[bold bright_green]you[/]").strip()
            except (KeyboardInterrupt, EOFError):
                return
            if not line:
                continue
            if line.startswith("/"):
                if not _handle_slash(session, line):
                    return
                continue
            _send(session, line)
        return

    run_chat(system=args.system, provider=args.provider, model=args.model)


if __name__ == "__main__":
    main()
