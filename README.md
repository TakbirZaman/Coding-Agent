# AI Coding Agent

I wanted a coding assistant that actually touches code, not just chats. So I built one that plans, edits files, runs commands, and checks its work with tests.

What it does:
- Reads / writes / edits files inside a sandboxed workspace
- Runs shell commands with a safety denylist
- Works with Gemini (free tier) or OpenAI, plus a mock mode with no key

Stack: Python, OpenAI function-calling, pytest, Docker

Run it:
```bash
pip install -e .
cp .env.example .env
# no key? use mock mode
set AGENT_MOCK=1
python -m ai_coding_agent.cli "summarize this repo" --workspace . --provider mock
```
