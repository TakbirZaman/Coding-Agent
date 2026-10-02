from pathlib import Path
from ai_coding_agent.agent import Agent
from ai_coding_agent.llm import LLM

class FakeLLM(LLM):
    def __init__(self):
        self.n = 0
    def chat(self, messages, tools):
        self.n += 1
        if self.n == 1:
            return {"content": "creating file",
                    "tool_calls": [{"id": "1", "name": "write_file",
                                    "args": {"path": "hello.txt", "content": "hi"}}]}
        return {"content": "done", "tool_calls": []}

def test_agent_writes_file(tmp_path):
    ag = Agent(tmp_path, llm=FakeLLM())
    out = ag.run("create hello.txt")
    assert out == "done"
    assert (tmp_path / "hello.txt").read_text() == "hi"
