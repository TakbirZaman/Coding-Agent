# Demo (30s, recruiter-friendly)

## Auto SVG (already in repo)
```
python examples/make_demo_svg.py
# -> docs/demo.svg
```
Embedded in README. Re-run after any CLI output change.

## Record real GIF (Windows, 2 min)
1. `winget install ScreenToGif`
2. Run in terminal (maximized, 80 cols):
```
$env:AGENT_MOCK="1"; $env:PYTHONPATH="src"
python -m ai_coding_agent.cli "add hello feature" --workspace . --max-steps 4
python -m pytest -q
```
3. ScreenToGif → Recorder → select terminal → Record → Stop → Save as `docs/demo.gif`
4. Keep GIF < 5MB, 15fps, 800px wide. Reference in README:
```md
![Demo](docs/demo.gif)
```
