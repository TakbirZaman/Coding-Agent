"""ReAct-style agent loop: think -> tool call -> observe, until done."""
from __future__ import annotations

import uuid
from pathlib import Path

from . import tools
from .llm import LLM, SYSTEM


class Agent:
    def __init__(self, workspace: Path, model: str | None = None,
                 provider: str = "auto", max_steps=12, llm: LLM | None = None):
        self.workspace = Path(workspace)
        self.max_steps = max_steps
        self.llm = llm or LLM(model=model, provider=provider)
        self.history: list = []

    def run(self, task: str) -> str:
        messages = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": task}]
        defs = tools.openai_tool_defs()
        for _ in range(self.max_steps):
            resp = self.llm.chat(messages, defs)
            for tc in resp["tool_calls"]:
                tc.setdefault("id", uuid.uuid4().hex[:8])
            messages.append({"role": "assistant", "content": resp["content"],
                             "tool_calls": resp["tool_calls"]})
            if not resp["tool_calls"]:
                self.history = messages
                return resp["content"]
            for tc in resp["tool_calls"]:
                out = tools.dispatch(tc["name"], self.workspace, tc["args"])
                messages.append({"role": "tool", "call_id": tc["id"],
                                 "name": tc["name"],
                                 "content": f"[{tc['name']}] {out}"})
        self.history = messages
        return "Stopped: max_steps reached. Summarize progress above."
