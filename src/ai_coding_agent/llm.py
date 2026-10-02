"""OpenAI client wrapper with mock mode for tests/demos."""
from __future__ import annotations
import json
import os

SYSTEM = "You are a senior coding agent. Plan, use tools, verify with tests."

class LLM:
    def __init__(self, model: str = "gpt-4o-mini", api_key: str | None = None):
        self.model = model
        self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        self.mock = not bool(self.api_key) or os.getenv("AGENT_MOCK") == "1"

    def chat(self, messages: list, tools: list) -> dict:
        if self.mock:
            return self._mock(messages)
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        r = client.chat.completions.create(model=self.model, messages=messages,
            tools=tools or None, tool_choice="auto" if tools else None)
        m = r.choices[0].message
        calls = []
        for tc in (m.tool_calls or []):
            calls.append({"id": tc.id, "name": tc.function.name,
                          "args": json.loads(tc.function.arguments or "{}")})
        return {"content": m.content or "", "tool_calls": calls}

    def _mock(self, messages: list) -> dict:
        # Deterministic demo: list dir, then finish. Tests override this.
        if len(messages) <= 2:
            return {"content": "Exploring workspace.",
                    "tool_calls": [{"id": "1", "name": "list_dir", "args": {"path": "."}}]}
        return {"content": "Done. Workspace explored, no changes needed.", "tool_calls": []}
