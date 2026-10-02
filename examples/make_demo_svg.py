"""Generate docs/demo.svg via Rich (no screen recorder needed)."""
from rich.console import Console

console = Console(record=True, width=80)

console.print("$ python -m ai_coding_agent.cli \"add hello feature\" --workspace .", style="bold green")
console.print("[dim]Agent: planning... (ReAct loop, max 12 steps)[/dim]")
console.print("[cyan]> tool list_dir[/cyan] path='.'")
console.print("  src/  tests/  README.md  pyproject.toml")
console.print("[cyan]> tool write_file[/cyan] path='hello.txt'")
console.print("  wrote 12 chars to hello.txt")
console.print("[cyan]> tool run_shell[/cyan] command='python -m pytest -q'")
console.print("  [exit 0] 4 passed in 0.12s", style="green")
console.print("[bold]Done. Added hello.txt and verified with pytest.[/bold]")
console.save_svg("docs/demo.svg", title="AI Coding Agent demo")
print("wrote docs/demo.svg")
