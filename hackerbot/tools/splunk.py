from pydantic import BaseModel, Field
from prettytable import PrettyTable, from_csv
import tempfile
import os
from warnings import warn
from typing import Generator, Literal
from splunklib import client
from splunklib import results
import logging
import time
import json

from hackerbot.tools.base_tool import (
    BaseTool,
    BaseToolConfig,
)
from hackerbot.exceptions import (
    GenerationError,
    QueryError,
    SplunkConnectionError,
)

logger: logging.Logger = logging.getLogger("hackerbot")


class SplunkRequest(BaseModel):
    question: str
    return_spl: bool = False

class SplunkResponse(BaseModel):
    answer: str
    spl: str | None = Field(None, description="The generated Splunk query")

class SplunkToolConfig(BaseToolConfig):
    splunk_host: str = Field(
        default = "127.0.0.1",
    )
    splunk_port: str | int = Field(
        default = 8089,
    )
    splunk_user: str = Field(
        default = "admin",
    )
    splunk_pass: str = Field(
        default = "password",
    )
    env_map: str = Field(
        default = "",
    )
    force_env_map_reload: bool = False


class SplunkTool(BaseTool):
    _config: SplunkToolConfig

    _splunk_service: client.Service | None = None

    def __init__(self,
        config: SplunkToolConfig,
    ):
        """
            Initialize the Splunk tool
            Capable of generating Splunk queries and running them in Splunk to then analyze the results using an LLM
        """
        super().__init__(config)

        self._config: SplunkToolConfig = config

        logger.debug(f"Initializing Splunk tool")

        if self._config.llm_model not in self._supported_models:
            raise ValueError(f"Model '{self._config.llm_model}' is not supported. Supported models: {self._supported_models}")

        logger.debug(f"Using LLM: {self._config.llm_model}")
        logger.debug(f"LLM URL: {self._config.llm_url}")

        if self._config.force_env_map_reload is True or self._config.env_map == "":
            self._config.env_map = self._map_env()

        logger.debug(f"Splunk environment map: {self._config.env_map}")

    def run(self, req: SplunkRequest) -> SplunkResponse:
        """
            Run the Splunk tool
            Generate a Splunk query based on the user input
            Run the query in Splunk
            Answer the user question based on the search results
        """
        logger.debug(f"Running Splunk tool with user input: {req.question}")

        self._question = req.question

        try:
            spl = self.generate_spl()
            logger.debug(f"Generated Splunk query: '{spl}'")
        except Exception as e:
            logger.error(f"Error generating Splunk query: {e}")
            raise GenerationError("Error generating Splunk query. Please try again later.")

        try:
            search_results = self.run_search(spl, output_mode='csv')
        except Exception as e:
            logger.error(f"Error running Splunk query: {e}")
            raise QueryError("Error running Splunk query. Please try again later.")

        self._search_results = "".join(search_results)

        try:
            answer = self.analyze_results()
        except ValueError as e:
            logger.error(f"Error answering user question: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error answering user question: {e}")
            raise GenerationError("Error answering user question. Please try again later.")

        return SplunkResponse(answer=answer, spl=spl if req.return_spl else None)

    def _prepare_generate_spl(self, question: str | None = None) -> list[dict[str, str]]:
        if question is None:
            if self._question is None:
                raise ValueError("Question is not set")
            question = self._question

        instructions = self._get_spl_generation_instructions()

        messages =[
            {
                'role': 'user',
                'content': instructions + "\nuser input:" + question
            },
        ]
        return messages

    def generate_spl(self, question: str | None = None) -> str:
        logger.debug("Generating Splunk query")

        messages = self._prepare_generate_spl(question=question)

        response = self._call_llm(messages=messages)

        spl = response['message']['content']

        logger.debug(f"Generated Splunk query: '{spl}'")

        return spl

    def stream_generate_spl(self, question: str | None = None) -> Generator[str, None, None]:
        logger.debug("Generating Splunk query")

        messages = self._prepare_generate_spl(question=question)

        response = self._stream_call_llm(messages=messages)
        for chunk in response:
            yield chunk['message']['content']

    def _get_splunk_service(self) -> client.Service:
        """
            Get the Splunk service object
        """
        logger.debug("Getting Splunk service object")

        if self._splunk_service is None:
            if not self._config.verify_ssl and not self._config.supress_warnings:
                warn(f"SSL verification is disabled when connecting to {self._config.splunk_host}:{self._config.splunk_port}. This is a security risk and should not be used in production.")
            try:
                self._splunk_service = client.connect(
                    host=self._config.splunk_host,
                    port=self._config.splunk_port,
                    username=self._config.splunk_user,
                    password=self._config.splunk_pass,
                    verify=self._config.verify_ssl,
                )
            except Exception as e:
                raise SplunkConnectionError(f"Error connecting to Splunk: {e}")

        return self._splunk_service

    def run_search(self, spl: str, output_mode: Literal['json', 'csv'] = 'csv') -> list[dict] | list[str]:
        """
            Run a Splunk search query
            Returns:
            - A list of dictionaries if output_mode is 'json'
            - A list of strings if output_mode is 'csv'. Each string is a row from the CSV
        """
        logger.debug("Running Splunk query")

        service = self._get_splunk_service()

        search_command = "search " + spl

        extra_kwargs = {
            'earliest_time' : '1',
            'latest_time' : 'now',
        }

        job = service.jobs.create(
            search_command,
            **extra_kwargs
        )


        while not job.is_done():
            time.sleep(2)
            pass

        events = []
        if output_mode == 'json':
            for result in results.JSONResultsReader(job.results(output_mode=output_mode)):
                if isinstance(result, results.Message):
                    # Diagnostic messages may be returned in the results
                    logger.debug(f'{result.type}: {result.message}')
                elif isinstance(result, dict):
                    # Normal events are returned as dicts
                    events.append(result)
                else:
                    logger.debug(f'Unknown result type: {result}')
        elif output_mode == 'csv':
            for result in job.results(output_mode=output_mode):
                if isinstance(result, results.Message):
                    # Diagnostic messages may be returned in the results
                    logger.debug(f'{result.type}: {result.message}')
                elif isinstance(result, str):
                    # Normal events are returned as strings
                    events.append(result)
                elif isinstance(result, bytes):
                    events.append(result.decode('utf-8'))

        logger.debug(f"Search results: '{events}'")
        return events

    def _map_env(self) -> str:
        logger.debug("Mapping Splunk envirnoment...")
        spl = "index!=_* |stats count by sourcetype |table sourcetype"
        env_map = json.dumps(self.run_search(spl, output_mode="json"))
        return str(env_map)

    @staticmethod
    def format_splunk_results_as_table(results: list[str | int | float] | list[dict], results_mode: Literal['json', 'csv'] = 'csv') -> PrettyTable:
        if results_mode not in ['json', 'csv']:
            raise ValueError(f"Invalid results_mode: '{results_mode}'. Must be 'json' or 'csv'")

        if results_mode == 'csv':
            # Checking that the results is in the shape that we want
            if not isinstance(results, list):
                raise TypeError("'results' must be a list when using results_mode = csv")
            for row in results:
                if not (isinstance(row, str) or isinstance(row, int) or isinstance(row, float)):
                    raise TypeError("All elements of 'results' must be either of str, int or float type when using results_mode = csv")

            # Check if the results are empty
            if len(results) == 0:
                return PrettyTable()

            with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
                tmp.writelines(results)
                tmp.close()

                with open(tmp.name, "r") as f:
                    table = from_csv(f)

                os.remove(tmp.name)

        elif results_mode == 'json':
            if not isinstance(results, list):
                raise TypeError("'results' must be a list when using results_mode = json")
            for row in results:
                if not (isinstance(row, dict)):
                    raise TypeError("All elements of 'results' must be of dict type when using results_mode = json")

            # Check if the results are empty
            if len(results) == 0:
                return PrettyTable()

            table = PrettyTable()
            # Aggregate valus from each line into a list for each column
            columns: dict[list[str]] = {}
            for line in results:
                for k, v in line.items():
                    if k not in columns:
                        columns[k] = []
                    # Try to convert the values to an int if possible. This is useful when sorting using these values
                    try:
                        v = float(v)
                        if v.as_integer_ratio()[1] == 1: # This is true when the float number can be an integer. e.g. 10.0 , 4124.0 etc.
                            v = int(v)
                    except:
                        pass
                    columns[k].append(v)

            for k, v in columns.items():
                table.add_column(k, v)

        # Set the sort key to 'count' if there is a count column
        if 'count' in table.field_names:
            table.sortby = 'count'

        return table


    def _get_spl_generation_instructions(self) -> str:
        """
            Get the instructions for generating a Splunk query
            Used to instruct the LLM model on how to generate the query
            Typically used by the generate_spl method
        """

        return '''
        You are part of a program that searches splunk
        Your Job is to create Splunk queries (SPL) based on the user input.
        Your response will be used as input to Splunk. therefore, respond only with a splunk SPL query. Nothing else.
        Do not output ANYTHING except the query itself. no explaination ot anything else. just the query iself

        use the following as examples:
        Show me events that happened on my AWS env -> index!=_* sourcetype=aws:cloudtrail | table _time user eventName eventSource _raw
        What users accessed my AWS cloud? -> index!=_* sourcetype=aws:cloudtrail | stats count by user
        Show me all users who accessed my system -> index!=_* |stats count by user, sourcetype
        What did john do in my cloud? -> index!=_* sourcetype=aws:cloudtrail user=john| stats count by user eventName eventSource
        What did user john do? -> index!=_* user=john | stats count by user src_ip command msg sourcetype
        What IP address did user mike use? -> index!=_* user=mike |stats count by user, src_ip
        what instances did john try to run? -> index!=_* sourcetype=aws:cloudtrail user=john command=RunInstances | table user eventName,eventSource, _raw
        what systems did user Mike access? -> index!=_* user=Mike | stats count by sourcetype
        show me the last 25 logs from cisco:asa that are associated with user john -> index!=_* sourcetype=cisco:asa user=john | head 25 | table _time, user, _raw
        show me all bash commands that were executed -> index!=_* sourcetype=bash_history | table _time,_raw
        show me traffic going to http, https and ssh going to 8.8.8.8 -> index!=_* dest_ip="8.8.8.8" AND (port=80 OR port=443 OR port=22) | table _time, src_ip, dest_ip, port, protocol
        show me traffic  going to 8.8.8.8 -> index!=_* dest_ip="8.8.8.8" | table _time, src_ip, dest_ip, port, protocol
        Instructions:
        - domains in the context of DNS could mean the "query" or the "hostname" fields
        - When asked about how a specific log type looks like, get a raw sample by using |head 10
        - When asked about sourcetypes or source references use the |metadata command
        - When asked about user's activities, do not use sourcetype in the query.
        - When asked about IP addresses, list all of them.
        - When asked about "count", or get "all" then use the stats commands instead of a table
        - Connect to mean dest_ip=
        - To show network traffic use |stats count by src_ip, src_port,dest_ip,dest_port
        - destination port means dest_port
        The following is useful information about the environment.
        ''' + str(self._config.env_map)
