from ai_coding_agent.llm import LLM


def test_auto_mock_without_keys(monkeypatch):
    for k in ("AGENT_MOCK", "GEMINI_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    llm = LLM(provider="auto")
    assert llm.provider == "mock"
    assert llm.mock


def test_auto_prefers_gemini(monkeypatch):
    for k in ("AGENT_MOCK", "GOOGLE_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "fake")
    llm = LLM(provider="auto")
    assert llm.provider == "gemini"
    assert llm.model == "gemini-2.5-flash"
    assert not llm.mock


def test_explicit_provider_respected(monkeypatch):
    monkeypatch.delenv("AGENT_MOCK", raising=False)
    assert LLM(provider="openai").provider == "openai"
    assert LLM(provider="mock").mock
