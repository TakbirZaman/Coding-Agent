"""ReAct-style agent loop: think -> tool call -> observe, until done."""
from __future__ import annotations
from pathlib import Path
from .llm import LLM, SYSTEM
from . import tools

class Agent:
    def __init__(self, workspace: Path, model="gpt-4o-mini", max_steps=12, llm: LLM | None = None):
        self.workspace = Path(workspace)
        self.max_steps = max_steps
        self.llm = llm or LLM(model=model)
        self.history: list = []

    def run(self, task: str) -> str:
        messages = [{"role": "system", "content": SYSTEM},
                    {"role": "user", "content": task}]
        defs = tools.openai_tool_defs()
        for _ in range(self.max_steps):
            resp = self.llm.chat(messages, defs)
            messages.append({"role": "assistant", "content": resp["content"]})
            if not resp["tool_calls"]:
                self.history = messages
                return resp["content"]
            for tc in resp["tool_calls"]:
                out = tools.dispatch(tc["name"], self.workspace, tc["args"])
                messages.append({"role": "tool", "content": f"[{tc['name']}] {out}"})
        self.history = messages
        return "Stopped: max_steps reached. Summarize progress above."
