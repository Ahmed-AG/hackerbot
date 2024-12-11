from typing import cast, Generator, Literal
from pydantic import BaseModel, Field
import logging
import boto3
from botocore.exceptions import ClientError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mypy_boto3_bedrock_runtime import (
        BedrockRuntimeClient,
    )
    from mypy_boto3_bedrock_runtime.type_defs import (
        ConverseResponseTypeDef,
        ConverseStreamOutputTypeDef,
    )
else:
    BedrockRuntimeClient = object
    ConverseResponseTypeDef = object
    ConverseStreamOutputTypeDef = object


logger = logging.getLogger("hackerbot")


bedrock_models = {
    "llama3.1": "us.meta.llama3-1-8b-instruct-v1:0",
    "llama3.1:70b": "us.meta.llama3-1-70b-instruct-v1:0",
    "llama3.1:405b": "us.meta.llama3-1-70b-instruct-v1:0",
}

class BaseToolConfig(BaseModel):
    llm_model: Literal[
        'llama3.1',
        'llama3.1:70b',
        'llama3.1:405b',
    ] = Field(
        default="llama3.1",
        description="The LLM model to use. Default is 'llama3.1'",
    )
    bedrock_region: Literal[
        "us-east-1",
        "us-east-2",
    ] = Field(
        default="us-east-2",
        description="The AWS region to use for calling Amazon Bedrock. Default is 'us-east-2'",
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

    _llm_client: BedrockRuntimeClient | None = None
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

    def _get_llm_client(self) -> BedrockRuntimeClient:
        """
            Get the LLM client
        """

        if self._llm_client is None:
            self._llm_client = boto3.client("bedrock-runtime", region_name=self._config.bedrock_region)
        return self._llm_client

    def _call_llm(self, messages: list[dict], system_prompt: str | None = None,  model: str | None = None) -> ConverseResponseTypeDef:
        """
            Call the LLM model
        """
        client = self._get_llm_client()
        if model is None:
            model = self._config.llm_model

        system = []
        if system_prompt:
            system.append({'text': system_prompt})
        response = client.converse(
            modelId=bedrock_models[model],
            messages=messages,
            system=system,
            inferenceConfig={
                "temperature": 0.0,
            }
        )

        logger.debug(f"LLM Response: {response}")

        return response

    def _stream_call_llm(self, messages: list[dict], system_prompt: str | None = None, model: str | None = None) -> Generator[ConverseStreamOutputTypeDef, None, None]:
        """
            Call the LLM model
        """
        client = self._get_llm_client()
        if model is None:
            model = self._config.llm_model

        system = []
        if system_prompt:
            system.append({'text': system_prompt})
        stream = client.converse_stream(
            modelId=bedrock_models[model],
            messages=messages,
            system=system,
            inferenceConfig={
                "temperature": 0.0,
            }
        )
        for chunk in stream['stream']:
            if "contentBlockDelta" in chunk:
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


        messages = [
            {
                'role': 'user',
                'content': [{"text": question}]
            },
        ]
        return messages

    def analyze_results(self, question: str | None = None, search_results: str | None = None) -> str:
        logger.debug("Answering user question")

        messages = self._prepare_analyze_results(question=question, search_results=search_results)

        instructions = self._get_analysis_instructions(search_results)

        response = self._call_llm(messages=messages, system_prompt=instructions)
        analysis = response['output']["message"]["content"][0]["text"]
        logger.debug(f"Splunk Task Analysis: '{analysis}'")
        return analysis

    def stream_analyze_results(self, question: str | None = None, search_results: str | None = None) -> Generator[str, None, None]:
        logger.debug("Answering user question")

        messages = self._prepare_analyze_results(question=question, search_results=search_results)

        instructions = self._get_analysis_instructions(search_results)

        response = self._stream_call_llm(messages=messages, system_prompt=instructions)
        for chunk in response:
            yield chunk['contentBlockDelta']["delta"]["text"]

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
