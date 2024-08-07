from pydantic import BaseModel, Field
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
from hackerbot.utilities import (
    env_var_config_default_factory,
)
from hackerbot.exceptions import (
    GenerationError,
    QueryError,
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
        default_factory=lambda: env_var_config_default_factory("splunk_host", "SPLUNK_HOST", error_on_empty=True),
    )
    splunk_port: str = Field(
        default_factory=lambda: env_var_config_default_factory("splunk_port", "SPLUNK_PORT", error_on_empty=True),
    )
    splunk_user: str = Field(
        default_factory=lambda: env_var_config_default_factory("splunk_user", "SPLUNK_USER", error_on_empty=True),
    )
    splunk_pass: str = Field(
        default_factory=lambda: env_var_config_default_factory("splunk_pass", "SPLUNK_PASS", error_on_empty=True),
    )
    use_static_env_map: bool = Field(
        default_factory=lambda: env_var_config_default_factory("use_static_env_map", "USE_SPLUNK_STATIC_ENV_MAP", error_on_empty=False).lower() == "true",
    )


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

        if self._config.use_static_env_map is True:
            self.env_map = '''
                {'sourcetypes': '[{"sourcetype": "PerfmonMk:Process"}, {"sourcetype": "Script:GetEndpointInfo"}, {"sourcetype": "Script:InstalledApps"}, {"sourcetype": "Script:ListeningPorts"}, {"sourcetype": "Unix:ListeningPorts"}, {"sourcetype": "Unix:SSHDConfig"}, {"sourcetype": "Unix:Service"}, {"sourcetype": "Unix:Update"}, {"sourcetype": "Unix:Uptime"}, {"sourcetype": "Unix:UserAccounts"}, {"sourcetype": "Unix:Version"}, {"sourcetype": "WinEventLog:Application"}, {"sourcetype": "WinEventLog:Microsoft-Windows-AppLocker/EXE and DLL"}, {"sourcetype": "WinEventLog:Microsoft-Windows-AppLocker/Packaged app-Execution"}, {"sourcetype": "WinEventLog:Microsoft-Windows-PowerShell/Operational"}, {"sourcetype": "WinEventLog:Security"}, {"sourcetype": "WinEventLog:System"}, {"sourcetype": "WinHostMon"}, {"sourcetype": "XmlWinEventLog:Microsoft-Windows-Sysmon/Operational"}, {"sourcetype": "access_combined"}, {"sourcetype": "alternatives"}, {"sourcetype": "amazon-ssm-agent"}, {"sourcetype": "amazon-ssm-agent-too_small"}, {"sourcetype": "apache_error"}, {"sourcetype": "aws:cloudtrail"}, {"sourcetype": "aws:cloudwatch"}, {"sourcetype": "aws:cloudwatch:guardduty"}, {"sourcetype": "aws:cloudwatchlogs"}, {"sourcetype": "aws:cloudwatchlogs:vpcflow"}, {"sourcetype": "aws:config:rule"}, {"sourcetype": "aws:description"}, {"sourcetype": "aws:elb:accesslogs"}, {"sourcetype": "aws:rds:audit"}, {"sourcetype": "aws:rds:error"}, {"sourcetype": "aws:s3:accesslogs"}, {"sourcetype": "bandwidth"}, {"sourcetype": "bash_history"}, {"sourcetype": "bootstrap"}, {"sourcetype": "cisco:asa"}, {"sourcetype": "cloud-init"}, {"sourcetype": "cloud-init-output"}, {"sourcetype": "code42:api"}, {"sourcetype": "code42:computer"}, {"sourcetype": "code42:org"}, {"sourcetype": "code42:security"}, {"sourcetype": "code42:user"}, {"sourcetype": "config_file"}, {"sourcetype": "cpu"}, {"sourcetype": "cron-too_small"}, {"sourcetype": "df"}, {"sourcetype": "dmesg"}, {"sourcetype": "dpkg"}, {"sourcetype": "error-too_small"}, {"sourcetype": "errors"}, {"sourcetype": "errors-too_small"}, {"sourcetype": "ess_content_importer"}, {"sourcetype": "hardware"}, {"sourcetype": "history-2"}, {"sourcetype": "interfaces"}, {"sourcetype": "iostat"}, {"sourcetype": "lastlog"}, {"sourcetype": "linux_audit"}, {"sourcetype": "linux_secure"}, {"sourcetype": "localhost-5"}, {"sourcetype": "lsof"}, {"sourcetype": "maillog-too_small"}, {"sourcetype": "ms:aad:audit"}, {"sourcetype": "ms:aad:signin"}, {"sourcetype": "ms:o365:management"}, {"sourcetype": "ms:o365:reporting:messagetrace"}, {"sourcetype": "netstat"}, {"sourcetype": "o365:management:activity"}, {"sourcetype": "openPorts"}, {"sourcetype": "osquery:info"}, {"sourcetype": "osquery:results"}, {"sourcetype": "osquery:warning"}, {"sourcetype": "out-3"}, {"sourcetype": "package"}, {"sourcetype": "protocol"}, {"sourcetype": "ps"}, {"sourcetype": "stream:arp"}, {"sourcetype": "stream:dhcp"}, {"sourcetype": "stream:dns"}, {"sourcetype": "stream:http"}, {"sourcetype": "stream:icmp"}, {"sourcetype": "stream:igmp"}, {"sourcetype": "stream:ip"}, {"sourcetype": "stream:mysql"}, {"sourcetype": "stream:smb"}, {"sourcetype": "stream:smtp"}, {"sourcetype": "stream:tcp"}, {"sourcetype": "stream:udp"}, {"sourcetype": "symantec:ep:agent:file"}, {"sourcetype": "symantec:ep:agt_system:file"}, {"sourcetype": "symantec:ep:behavior:file"}, {"sourcetype": "symantec:ep:packet:file"}, {"sourcetype": "symantec:ep:risk:file"}, {"sourcetype": "symantec:ep:scm_system:file"}, {"sourcetype": "symantec:ep:security:file"}, {"sourcetype": "symantec:ep:traffic:file"}, {"sourcetype": "syslog"}, {"sourcetype": "time"}, {"sourcetype": "top"}, {"sourcetype": "usersWithLoginPrivs"}, {"sourcetype": "vmstat"}, {"sourcetype": "who"}, {"sourcetype": "yum-too_small"}]'}
                '''
        else:
            self.env_map = self._map_env()

        logger.debug(f"Splunk environment map: {self.env_map}")

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
            self._splunk_service = client.connect(
                host=self._config.splunk_host,
                port=self._config.splunk_port,
                username=self._config.splunk_user,
                password=self._config.splunk_pass,
                verify=self._config.verify_ssl,
            )

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
        env_map = json.dumps(json.loads(self.run_search(spl))[0])
        return str(env_map)

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
        Instructions:
        - When asked about user's activities, do not use sourcetype in the query.
        - When asked about IP addresses, list all of them.
        - When asked about "count", or get "all" then use the stats commands instead of a table
        - Connect to mean dest_ip=
        - To show network traffic use |stats count by src_ip, src_port,dest_ip,dest_port
        The following is useful information about the environment.
        ''' + str(self.env_map)
