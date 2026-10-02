"""CLI entry point."""
import argparse
from pathlib import Path

from .agent import Agent


def main():
    ap = argparse.ArgumentParser(description="AI Coding Agent (Gemini/OpenAI + tools)")
    ap.add_argument("task", help="Task, e.g. 'add tests for tools.py'")
    ap.add_argument("--workspace", default=".", help="Sandbox dir for file ops")
    ap.add_argument("--provider", default="auto", choices=["auto", "gemini", "openai", "mock"],
                    help="LLM provider (auto: Gemini key > OpenAI key > mock)")
    ap.add_argument("--model", default=None,
                    help="Model override (default: gemini-2.5-flash / gpt-4o-mini)")
    ap.add_argument("--max-steps", type=int, default=12)
    a = ap.parse_args()
    ag = Agent(Path(a.workspace), model=a.model, provider=a.provider,
               max_steps=a.max_steps)
    print(f"[provider: {ag.llm.provider}, model: {ag.llm.model}]")
    print(ag.run(a.task))


if __name__ == "__main__":
    main()
