import pytest
from pytest import MonkeyPatch

from hackerbot.tools.base_tool import BaseTool, BaseToolConfig

def test_prepare_analyze_results_raises_value_error_when_question_is_missing(set_default_llm_url):
    tool = BaseTool(BaseToolConfig())
    with pytest.raises(ValueError) as e:
        tool._prepare_analyze_results(search_results="search_results")
    assert str(e.value) == "Question is not set"

def test_prepare_analyze_results_raises_value_error_when_search_results_is_missing(set_default_llm_url):
    tool = BaseTool(BaseToolConfig())
    with pytest.raises(ValueError) as e:
        tool._prepare_analyze_results(question="question")
    assert str(e.value) == "Search results is not set"

def test_config_verify_ssl_is_true_by_default(monkeypatch: MonkeyPatch, set_default_llm_url):
    monkeypatch.delenv("VERIFY_SSL", raising=False)

    config = BaseToolConfig()
    assert config.verify_ssl is True

def test_config_verify_ssl_is_false_when_env_var_is_false(monkeypatch: MonkeyPatch, set_default_llm_url):
    monkeypatch.setenv("VERIFY_SSL", "false")

    config = BaseToolConfig()
    assert config.verify_ssl is False, "BaseToolConfig.verify_ssl should be False when VERIFY_SSL env var is set to 'false'"

    monkeypatch.setenv("VERIFY_SSL", "FALSE")

    config = BaseToolConfig()
    assert config.verify_ssl is False, "BaseToolConfig.verify_ssl should be False when VERIFY_SSL env var is set to 'false'"

    monkeypatch.setenv("VERIFY_SSL", "FaLsE")

    config = BaseToolConfig()
    assert config.verify_ssl is False, "BaseToolConfig.verify_ssl should be False when VERIFY_SSL env var is set to 'false'"

def test_analyze_results_calls_prepare_analyze_results(monkeypatch: MonkeyPatch, set_default_llm_url):

    def mock_prepare_analyze_results(*args, **lwargs):
        return [
            {
                "role": "user",
                "content": "This is a user question with instructions"
            }
        ]

    def mock_call_llm(*args, **lwargs):
        return {
            "message": {
                "content": "This is the response from the LLM model"
            }
        }

    monkeypatch.setattr(BaseTool, "_prepare_analyze_results", mock_prepare_analyze_results)
    monkeypatch.setattr(BaseTool, "_call_llm", mock_call_llm)


    tool = BaseTool(BaseToolConfig())
    assert tool.analyze_results("question", "search_results") == "This is the response from the LLM model"

def test_stream_analyze_results_calls_prepare_analyze_results(monkeypatch: MonkeyPatch, set_default_llm_url):


    chunks = [
        {"message": {"content": "This is response Nr. 1 from the LLM model"}},
        {"message": {"content": "This is response Nr. 2 from the LLM model"}},
        {"message": {"content": "This is response Nr. 3 from the LLM model"}},
        {"message": {"content": "This is response Nr. 4 from the LLM model"}},
        {"message": {"content": "This is response Nr. 5 from the LLM model"}},
        {"message": {"content": "This is response Nr. 6 from the LLM model"}},
        {"message": {"content": "This is response Nr. 7 from the LLM model"}},
        {"message": {"content": "This is response Nr. 8 from the LLM model"}},
    ]

    def mock_stream_call_llm(*args, **lwargs):
        for chunk in chunks:
            yield chunk

    monkeypatch.setattr(BaseTool, "_stream_call_llm", mock_stream_call_llm)


    tool = BaseTool(BaseToolConfig())
    for i, chunk in enumerate(tool.stream_analyze_results("question", "search_results")):
        assert chunk == chunks[i]["message"]["content"]
