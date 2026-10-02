"""Tool registry with sandboxing for the coding agent."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

BLOCKED_COMMANDS = ("rm -rf", "mkfs", "dd if=", ":(){", "shutdown", "reboot", "takeown", "format ")

def _resolve(workspace: Path, target: str) -> Path:
    p = (workspace / target).resolve() if not os.path.isabs(target) else Path(target).resolve()
    ws = workspace.resolve()
    if ws not in p.parents and p != ws:
        raise ValueError(f"Path escape blocked: {target}")
    return p

def read_file(workspace: Path, path: str) -> str:
    f = _resolve(workspace, path)
    return f.read_text(encoding="utf-8")[:20000]

def list_dir(workspace: Path, path: str = ".") -> str:
    d = _resolve(workspace, path)
    return "\n".join(sorted(x.name + ("/" if x.is_dir() else "") for x in d.iterdir()))

def write_file(workspace: Path, path: str, content: str) -> str:
    f = _resolve(workspace, path)
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    return f"wrote {len(content)} chars to {path}"

def edit_file(workspace: Path, path: str, old: str, new: str) -> str:
    f = _resolve(workspace, path)
    text = f.read_text(encoding="utf-8")
    if old not in text:
        raise ValueError("oldString not found")
    f.write_text(text.replace(old, new, 1), encoding="utf-8")
    return f"edited {path}"

def run_shell(workspace: Path, command: str, timeout: int = 30) -> str:
    low = command.lower()
    if any(b in low for b in BLOCKED_COMMANDS):
        raise ValueError("Blocked dangerous command")
    r = subprocess.run(command, shell=True, cwd=str(workspace),
                        capture_output=True, text=True, timeout=timeout, check=False)
    out = (r.stdout + r.stderr)[-8000:]
    return f"[exit {r.returncode}]\n{out}"

TOOLS = [
    {"name": "read_file", "fn": read_file,
     "schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]},
     "desc": "Read a file from workspace"},
    {"name": "list_dir", "fn": list_dir,
     "schema": {"type": "object", "properties": {"path": {"type": "string"}}},
     "desc": "List directory contents"},
    {"name": "write_file", "fn": write_file,
     "schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]},
     "desc": "Create/overwrite a file"},
    {"name": "edit_file", "fn": edit_file,
     "schema": {"type": "object", "properties": {"path": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}}, "required": ["path", "old", "new"]},
     "desc": "Exact-string replace in a file"},
    {"name": "run_shell", "fn": run_shell,
     "schema": {"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]},
     "desc": "Run a safe shell command (pytest, npm, git, python)"},
]

def openai_tool_defs() -> list:
    return [{"type": "function", "function": {
        "name": t["name"], "description": t["desc"], "parameters": t["schema"]}} for t in TOOLS]

def dispatch(name: str, workspace: Path, args: dict) -> str:
    for t in TOOLS:
        if t["name"] == name:
            try:
                return str(t["fn"](workspace, **args))
            except Exception as e:  # noqa: BLE001 - tool errors must return, not crash agent
                return f"ERROR: {e}"
    return f"ERROR: unknown tool {name}"
