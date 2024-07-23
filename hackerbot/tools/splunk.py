from pydantic import BaseModel, Field
from ollama import Client
import logging
import requests
import time
import json
import os
import uuid
import warnings

from hackerbot.tools.base_tool import BaseTool
from hackerbot.exceptions import (
    GenerationError,
)

logger: logging.Logger = logging.getLogger("hackerbot")


class SplunkRequest(BaseModel):
    question: str
    return_spl: bool = False

class SplunkResponse(BaseModel):
    answer: str
    spl: str | None = Field(None, description="The generated Splunk query")


class Splunk(BaseTool):
    def __init__(self,
        *,
        llm_model: str = "llama3",
        llm_url: str | None = None,
        splunk_host: str | None = None,
        splunk_port: str | None = None,
        splunk_user: str | None = None,
        splunk_pass: str | None = None,
        verify_ssl: bool | None  = None,
        use_static_env_map: bool | None = None,
    ):
        """
        """
        self._llm_url = llm_url or os.getenv('LLM_URL')
        assert self._llm_url is not None, "llm_url must be passed as an argument of an environmental variable ('LLM_URL')"

        self._splunk_host = splunk_host or os.getenv('SPLUNK_HOST')
        assert self._splunk_host is not None, "splunk_host must be passed as an argument of an environmental variable ('SPLUNK_HOST')"

        self._splunk_port = splunk_port or os.getenv('SPLUNK_PORT')
        assert self._splunk_port is not None, "splunk_port must be passed as an argument of an environmental variable ('SPLUNK_PORT')"

        self._splunk_user = splunk_user or os.getenv('SPLUNK_USER')
        assert self._splunk_user is not None, "splunk_user must be passed as an argument of an environmental variable ('SPLUNK_USER')"

        self._splunk_pass = splunk_pass or os.getenv('SPLUNK_PASS')
        assert self._splunk_pass is not None, "splunk_pass must be passed as an argument of an environmental variable ('SPLUNK_PASS')"

        self._verify_ssl = verify_ssl or os.getenv('VERIFY_SSL', 'True').lower() == 'true'
        if self._verify_ssl is False:
            requests.packages.urllib3.disable_warnings()
            warnings.warn("SSL verification is disabled. This is a security risk and should not be used in production.")

        self._use_static_env_map = use_static_env_map or os.getenv('USE_SPLUNK_STATIC_ENV_MAP', 'False').lower() == 'true'

        if llm_model not in self._supported_models:
            raise ValueError(f"Model '{llm_model}' is not supported. Supported models: {self._supported_models}")
        self._llm_model = llm_model

        logger.debug(f"Using LLM: {self._llm_model}")

        self._llm_client: Client | None = None


        if self._use_static_env_map is True:
            self.env_map = '''
                {'sourcetypes': '[{"sourcetype": "PerfmonMk:Process"}, {"sourcetype": "Script:GetEndpointInfo"}, {"sourcetype": "Script:InstalledApps"}, {"sourcetype": "Script:ListeningPorts"}, {"sourcetype": "Unix:ListeningPorts"}, {"sourcetype": "Unix:SSHDConfig"}, {"sourcetype": "Unix:Service"}, {"sourcetype": "Unix:Update"}, {"sourcetype": "Unix:Uptime"}, {"sourcetype": "Unix:UserAccounts"}, {"sourcetype": "Unix:Version"}, {"sourcetype": "WinEventLog:Application"}, {"sourcetype": "WinEventLog:Microsoft-Windows-AppLocker/EXE and DLL"}, {"sourcetype": "WinEventLog:Microsoft-Windows-AppLocker/Packaged app-Execution"}, {"sourcetype": "WinEventLog:Microsoft-Windows-PowerShell/Operational"}, {"sourcetype": "WinEventLog:Security"}, {"sourcetype": "WinEventLog:System"}, {"sourcetype": "WinHostMon"}, {"sourcetype": "XmlWinEventLog:Microsoft-Windows-Sysmon/Operational"}, {"sourcetype": "access_combined"}, {"sourcetype": "alternatives"}, {"sourcetype": "amazon-ssm-agent"}, {"sourcetype": "amazon-ssm-agent-too_small"}, {"sourcetype": "apache_error"}, {"sourcetype": "aws:cloudtrail"}, {"sourcetype": "aws:cloudwatch"}, {"sourcetype": "aws:cloudwatch:guardduty"}, {"sourcetype": "aws:cloudwatchlogs"}, {"sourcetype": "aws:cloudwatchlogs:vpcflow"}, {"sourcetype": "aws:config:rule"}, {"sourcetype": "aws:description"}, {"sourcetype": "aws:elb:accesslogs"}, {"sourcetype": "aws:rds:audit"}, {"sourcetype": "aws:rds:error"}, {"sourcetype": "aws:s3:accesslogs"}, {"sourcetype": "bandwidth"}, {"sourcetype": "bash_history"}, {"sourcetype": "bootstrap"}, {"sourcetype": "cisco:asa"}, {"sourcetype": "cloud-init"}, {"sourcetype": "cloud-init-output"}, {"sourcetype": "code42:api"}, {"sourcetype": "code42:computer"}, {"sourcetype": "code42:org"}, {"sourcetype": "code42:security"}, {"sourcetype": "code42:user"}, {"sourcetype": "config_file"}, {"sourcetype": "cpu"}, {"sourcetype": "cron-too_small"}, {"sourcetype": "df"}, {"sourcetype": "dmesg"}, {"sourcetype": "dpkg"}, {"sourcetype": "error-too_small"}, {"sourcetype": "errors"}, {"sourcetype": "errors-too_small"}, {"sourcetype": "ess_content_importer"}, {"sourcetype": "hardware"}, {"sourcetype": "history-2"}, {"sourcetype": "interfaces"}, {"sourcetype": "iostat"}, {"sourcetype": "lastlog"}, {"sourcetype": "linux_audit"}, {"sourcetype": "linux_secure"}, {"sourcetype": "localhost-5"}, {"sourcetype": "lsof"}, {"sourcetype": "maillog-too_small"}, {"sourcetype": "ms:aad:audit"}, {"sourcetype": "ms:aad:signin"}, {"sourcetype": "ms:o365:management"}, {"sourcetype": "ms:o365:reporting:messagetrace"}, {"sourcetype": "netstat"}, {"sourcetype": "o365:management:activity"}, {"sourcetype": "openPorts"}, {"sourcetype": "osquery:info"}, {"sourcetype": "osquery:results"}, {"sourcetype": "osquery:warning"}, {"sourcetype": "out-3"}, {"sourcetype": "package"}, {"sourcetype": "protocol"}, {"sourcetype": "ps"}, {"sourcetype": "stream:arp"}, {"sourcetype": "stream:dhcp"}, {"sourcetype": "stream:dns"}, {"sourcetype": "stream:http"}, {"sourcetype": "stream:icmp"}, {"sourcetype": "stream:igmp"}, {"sourcetype": "stream:ip"}, {"sourcetype": "stream:mysql"}, {"sourcetype": "stream:smb"}, {"sourcetype": "stream:smtp"}, {"sourcetype": "stream:tcp"}, {"sourcetype": "stream:udp"}, {"sourcetype": "symantec:ep:agent:file"}, {"sourcetype": "symantec:ep:agt_system:file"}, {"sourcetype": "symantec:ep:behavior:file"}, {"sourcetype": "symantec:ep:packet:file"}, {"sourcetype": "symantec:ep:risk:file"}, {"sourcetype": "symantec:ep:scm_system:file"}, {"sourcetype": "symantec:ep:security:file"}, {"sourcetype": "symantec:ep:traffic:file"}, {"sourcetype": "syslog"}, {"sourcetype": "time"}, {"sourcetype": "top"}, {"sourcetype": "usersWithLoginPrivs"}, {"sourcetype": "vmstat"}, {"sourcetype": "who"}, {"sourcetype": "yum-too_small"}]'}
                '''
        else:
            self.env_map = self.map_env()

        logger.debug(f"Splunk environment map: {self.env_map}")

    def run(self, req: SplunkRequest) -> SplunkResponse:
        """
            Run the Splunk tool
            Generate a Splunk query based on the user input
            Run the query in Splunk
            Answer the user question based on the search results
        """
        logger.debug(f"Running Splunk tool with user input: {req.question}")

        try:
            spl = self.generate_spl(req.question)
        except Exception as e:
            logger.error(f"Error generating Splunk query: {e}")
            raise GenerationError("Error generating Splunk query. Please try again later.")


        results = self.run_search(spl)


        try:
            answer = self.answer_user_question(req.question, results)
        except Exception as e:
            logger.error(f"Error answering user question: {e}")
            raise GenerationError("Error answering user question. Please try again later.")

        return SplunkResponse(answer=answer, spl=spl if req.return_spl else None)

    def generate_spl(self, user_input):
        logger.debug("Generating Splunk query")

        client = self._get_llm_client()
        instructions = '''
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
        Instructions:
        - When asked about user's activities, do not use sourcetype in the query.
        - When asked about IP addresses, list all of them.
        - When asked about "count", or get "all" then use the stats commands instead of a table
        The following is useful information about the environment.
        ''' + str(self.env_map)

        response = client.chat(model=self._llm_model, messages=[
                {
                    'role': 'user',
                    'content': instructions + "\nuser input:" + user_input
                },
            ]
        )

        self._log_model_metrics(response)

        spl = response['message']['content']

        logger.debug(f"Generated Splunk query: '{spl}'")

        return spl


    def run_search(self, spl: str):
        logger.debug("Running Splunk query")

        scheme = 'https'
        search_command = "search " + spl

        unique_id  = uuid.uuid4().hex

        post_data = { 'id' : unique_id,
                    'search' : search_command,
                    'earliest_time' : '1',
                    'latest_time' : 'now',
                    }

        splunk_search_base_url =  f"{scheme}://{self._splunk_host}:{self._splunk_port}/servicesNS/{self._splunk_user}/search/search/jobs"
        resp = requests.post(splunk_search_base_url, data = post_data, verify = self._verify_ssl, auth = (self._splunk_user, self._splunk_pass))

        # print(resp.text)

        is_job_completed = ''

        while(is_job_completed != 'DONE'):
            time.sleep(5)
            get_data = {'output_mode' : 'json'}
            job_status_base_url = f"{scheme}://{self._splunk_host}:{self._splunk_port}/servicesNS/{self._splunk_user}/search/search/jobs/{unique_id}"
            resp_job_status = requests.post(job_status_base_url, data = get_data, verify = self._verify_ssl, auth = (self._splunk_user, self._splunk_pass))
            print(resp_job_status)
            resp_job_status_data = resp_job_status.json()
            is_job_completed = resp_job_status_data['entry'][0]['content']['dispatchState']
            print("Current job status is {}".format(is_job_completed))

        splunk_summary_base_url = f"{scheme}://{self._splunk_host}:{self._splunk_port}/servicesNS/{self._splunk_user}/search/search/jobs/{unique_id}/results?count=0"
        splunk_summary_results = requests.get(splunk_summary_base_url, data = get_data, verify = self._verify_ssl, auth = (self._splunk_user, self._splunk_pass))
        splunk_summary_data = splunk_summary_results.json()


        results = json.dumps(splunk_summary_data['results'])
        logger.debug(f"Search results: '{results}'")
        return results

    def answer_user_question(self, question, search_results):

        logger.debug("Answering user question")

        client = self._get_llm_client()
        instructions = f'''
        Your Job is to read the User Question and the Search Results, then answer the User Question based on the search results.
        Instructions:
        - Keep your answers short and straight to the point.
        - If you do not understand the question, summerize the search results.
        - If search results is emply, just say "No search data was returned".
        '''
        response = client.chat(model=self._llm_model, messages=[
                {
                    'role': 'user',
                    'content': instructions + "\nUser Question: " + question + "\nSearch Results:\n" + search_results
                },
            ]
        )

        self._log_model_metrics(response)

        analysis = response['message']['content']

        logger.debug(f"Answer: '{analysis}'")
        return analysis

    def map_env(self) -> str:
        logger.debug("Mapping Splunk envirnoment...")
        spl = "index!=_* |stats count by sourcetype |table sourcetype"
        env_map = json.dumps(json.loads(self.run_search(spl))[0])
        return str(env_map)
