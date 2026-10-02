"""LLM client: OpenAI + Gemini tool-calling, with mock mode for tests/demos."""
from __future__ import annotations

import json
import os
import uuid

SYSTEM = "You are a senior coding agent. Plan, use tools, verify with tests."
OPENAI_DEFAULT_MODEL = "gpt-4o-mini"
GEMINI_DEFAULT_MODEL = "gemini-2.5-flash"


class LLM:
    def __init__(self, model: str | None = None, api_key: str | None = None,
                 provider: str = "auto"):
        self.provider = self._detect(provider)
        if self.provider == "gemini":
            self.model = model or os.getenv("GEMINI_MODEL", GEMINI_DEFAULT_MODEL)
            self.api_key = (api_key or os.getenv("GEMINI_API_KEY", "")
                            or os.getenv("GOOGLE_API_KEY", ""))
        elif self.provider == "openai":
            self.model = model or os.getenv("OPENAI_MODEL", OPENAI_DEFAULT_MODEL)
            self.api_key = api_key or os.getenv("OPENAI_API_KEY", "")
        else:
            self.model = model or "mock"
            self.api_key = ""
        self.mock = (self.provider == "mock")

    @staticmethod
    def _detect(provider: str) -> str:
        if os.getenv("AGENT_MOCK") == "1":
            return "mock"
        if provider in ("openai", "gemini", "mock"):
            return provider
        if os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", ""):
            return "gemini"
        if os.getenv("OPENAI_API_KEY", ""):
            return "openai"
        return "mock"

    def chat(self, messages: list, tools: list) -> dict:
        if self.provider == "gemini":
            return self._gemini_chat(messages, tools)
        if self.provider == "openai":
            return self._openai_chat(messages, tools)
        return self._mock(messages)

    # ----- OpenAI -----
    def _openai_chat(self, messages: list, tools: list) -> dict:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key)
        payload = []
        for m in messages:
            role = m["role"]
            if role == "system" or role == "user":
                payload.append({"role": role, "content": m.get("content", "")})
            elif role == "assistant":
                d: dict = {"role": "assistant", "content": m.get("content", "")}
                if m.get("tool_calls"):
                    d["tool_calls"] = [{
                        "id": tc["id"], "type": "function",
                        "function": {"name": tc["name"],
                                     "arguments": json.dumps(tc.get("args", {}))},
                    } for tc in m["tool_calls"]]
                payload.append(d)
            elif role == "tool":
                payload.append({"role": "tool", "tool_call_id": m["call_id"],
                                "content": m.get("content", "")})
        r = client.chat.completions.create(
            model=self.model, messages=payload,
            tools=tools or None, tool_choice="auto" if tools else None)
        m = r.choices[0].message
        calls = [{"id": tc.id, "name": tc.function.name,
                  "args": json.loads(tc.function.arguments or "{}")}
                 for tc in (m.tool_calls or [])]
        return {"content": m.content or "", "tool_calls": calls}

    # ----- Gemini -----
    def _gemini_chat(self, messages: list, tools: list) -> dict:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=self.api_key)
        decls = []
        for d in (tools or []):
            f = d.get("function", d)
            decls.append(types.FunctionDeclaration(
                name=f["name"], description=f.get("description", ""),
                parameters=f.get("parameters", {"type": "object",
                                                "properties": {}})))
        contents, pending = [], {}
        for m in messages:
            role = m["role"]
            if role == "system":
                continue
            elif role == "user":
                contents.append({"role": "user",
                                 "parts": [{"text": m.get("content", "")}]})
            elif role == "assistant":
                parts = []
                if m.get("content"):
                    parts.append({"text": m["content"]})
                for tc in m.get("tool_calls", []):
                    pending[tc["id"]] = tc["name"]
                    parts.append({"function_call": {"name": tc["name"],
                                                   "args": tc.get("args", {})}})
                contents.append({"role": "model", "parts": parts})
            elif role == "tool":
                name = m.get("name") or pending.pop(m["call_id"], "unknown")
                contents.append({"role": "user", "parts": [{
                    "function_response": {"name": name,
                                         "response": {"result": m.get(
                                             "content", "")}}}]})
        tool_cfg = ([types.Tool(function_declarations=decls)]
                    if decls else None)
        resp = client.models.generate_content(
            model=self.model, contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM, tools=tool_cfg))
        if not resp.candidates:
            return {"content": "", "tool_calls": []}
        text, calls = [], []
        for p in resp.candidates[0].content.parts:
            fc = getattr(p, "function_call", None)
            if fc:
                try:
                    args = json.loads(json.dumps(fc.args, default=str))
                except (TypeError, ValueError):
                    args = {}
                calls.append({"id": uuid.uuid4().hex[:8],
                              "name": fc.name, "args": args})
            elif getattr(p, "text", None):
                text.append(p.text)
        return {"content": "".join(text), "tool_calls": calls}

    def _mock(self, messages: list) -> dict:
        # Deterministic demo: list dir, then finish. Tests override this.
        if len(messages) <= 2:
            return {"content": "Exploring workspace.",
                    "tool_calls": [{"id": "1", "name": "list_dir",
                                    "args": {"path": "."}}]}
        return {"content": "Done. Workspace explored, no changes needed.",
                "tool_calls": []}
