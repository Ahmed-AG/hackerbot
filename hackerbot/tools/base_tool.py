from ollama import Client, ChatResponse
from typing import cast, Generator, Literal
from pydantic import BaseModel, Field
import logging


logger = logging.getLogger("hackerbot")


class BaseToolConfig(BaseModel):
    llm_model: Literal[
        'llama3',
        'llama3.1',
        'llama3.1:70b',
        'llama3.1:405b',
    ] = Field(
        default="llama3.1",
        description="The LLM model to use. Can be 'llama3' or 'llama3.1'. Default is 'llama3.1'",
    )
    llm_url: str = Field(
        default = "http://localhost:11434",
    )
    verify_ssl: bool = Field(
        default = True,
    )
    supress_warnings: bool = Field(
        default = False,
    )


class BaseTool:
    _supported_models: list[str] = ["llama3", "llama3.1", "llama3.1:70b", "llama3.1:405b"]

    _llm_client: Client | None = None
    _config: BaseToolConfig

    _question: str | None = None
    _search_results: str | None = None

    def __init__(self, config: BaseToolConfig) -> None:
        self._config = config

        if self._config.llm_model not in self._supported_models:
            raise ValueError(f"Model '{self._config.llm_model}' is not supported")


        if self._config.verify_ssl is False:
            try:
                import requests
                requests.packages.urllib3.disable_warnings()
            except ImportError:
                pass

    def _get_llm_client(self) -> Client:
        """
            Get the LLM client
        """
        assert self._config.llm_url is not None, "LLM URL is not set"

        if self._llm_client is None:
            self._llm_client = Client(host=self._config.llm_url)
        return self._llm_client

    def _log_model_metrics(self, response: ChatResponse) -> None:
        logger.debug("Logging model metrics")

        if self._config.llm_model == "llama3":
            self._log_llama3_metrics(response)
        elif self._config.llm_model == "llama3.1":
            self._log_llama3_metrics(response)
        else:
            logger.warning(f"No metrics logging for model {self._config.llm_model} defined")

    @staticmethod
    def _log_llama3_metrics(response: ChatResponse) -> None:
        total_duration = response.get('total_duration')
        if total_duration is not None:
            total_duration = response.get('total_duration') / 1_000_000_000
        else:
            total_duration = 'N/A'

        load_duration = response.get('load_duration')
        if load_duration is not None:
            load_duration = response.get('load_duration') / 1_000_000_000
        else:
            load_duration = 'N/A'

        logger.debug(f"Total Duration: {total_duration} seconds")
        logger.debug(f"Load Duration: {load_duration} seconds")

    def _call_llm(self, messages: list[dict],  model: str | None = None) -> ChatResponse:
        """
            Call the LLM model
        """
        client = self._get_llm_client()
        if model is None:
            model = self._config.llm_model
        # TODO: use generate instead of chat
        response = client.chat(model=model, messages=messages)
        typed_response = cast(ChatResponse, response)

        logger.debug(f"LLM Response: {typed_response}")
        self._log_model_metrics(typed_response)

        return typed_response

    def _stream_call_llm(self, messages: list[dict],  model: str | None = None) -> Generator[ChatResponse, None, None]:
        """
            Call the LLM model
        """
        client = self._get_llm_client()
        if model is None:
            model = self._config.llm_model
        stream = client.chat(model=model, messages=messages, stream=True)
        for chunk in stream:
            yield chunk

    def _prepare_analyze_results(self, question: str | None = None, search_results: str | None = None) -> list[dict[str, str]]:
        # Check if question is set. Use the question set in the class if not
        if question is None:
            if self._question is None:
                raise ValueError("Question is not set")
            question = self._question

        # Check if search results is set. Use the search results set in the class if not
        if search_results is None:
            if self._search_results is None:
                raise ValueError("Search results is not set")
            search_results = self._search_results


        instructions = self._get_analysis_instructions(search_results)

        messages = [
            {
                'role': 'system',
                'content': instructions
            },
            {
                'role': 'user',
                'content': question
            },
        ]
        return messages

    def analyze_results(self, question: str | None = None, search_results: str | None = None) -> str:
        logger.debug("Answering user question")

        messages = self._prepare_analyze_results(question=question, search_results=search_results)

        response = self._call_llm(messages=messages)
        analysis = response["message"]["content"]
        logger.debug(f"Splunk Task Analysis: '{analysis}'")
        return analysis

    def stream_analyze_results(self, question: str | None = None, search_results: str | None = None) -> Generator[str, None, None]:
        logger.debug("Answering user question")

        messages = self._prepare_analyze_results(question=question, search_results=search_results)

        response = self._stream_call_llm(messages=messages)
        for chunk in response:
            yield chunk['message']['content']

    def _get_analysis_instructions(self, search_results: str) -> str:
        """
            Get the analysis instructions
            Used to instruct the LLM model on how to analyze the data
            Typically used by the analyze_results method
        """

        return f"""
                You are an expert cyber security analyst.
                Your Job is to read and understand the Search results and answer the User Question based on your expertise and understanding of the search results.


                Field of Expertise:
                    - Cyber Security
                    - Splunk Analysis
                    - Incident Investigation
                    - Threat Intelligence

                Give your final best answer, following these rules:
                    - Keep your answers short and straight to the point.
                    - If you do not understand the question, summerize the search results.
                    - If search results is emply, just say "No search data was returned".
                    - Do not use XML Tags in your answer.


                <search results>
                {search_results}
                </search results>
            """
