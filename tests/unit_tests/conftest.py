import pytest

from hackerbot.tools.base_tool import BaseToolConfig

@pytest.fixture(scope="function")
def default_base_tool_config():
    return BaseToolConfig(
        llm_url="https://llm.example.com",
    )

@pytest.fixture(scope="function")
def set_default_llm_url(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("LLM_URL", "https://llm.example.com")
