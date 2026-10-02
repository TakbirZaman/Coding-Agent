"""CLI entry point."""
import argparse
from pathlib import Path
from .agent import Agent

def main():
    ap = argparse.ArgumentParser(description="AI Coding Agent (OpenAI + tools)")
    ap.add_argument("task", help="Task, e.g. 'add tests for tools.py'")
    ap.add_argument("--workspace", default=".", help="Sandbox dir for file ops")
    ap.add_argument("--model", default="gpt-4o-mini")
    ap.add_argument("--max-steps", type=int, default=12)
    a = ap.parse_args()
    ag = Agent(Path(a.workspace), model=a.model, max_steps=a.max_steps)
    print(ag.run(a.task))

if __name__ == "__main__":
    main()
