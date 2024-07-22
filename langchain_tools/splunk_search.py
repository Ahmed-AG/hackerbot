
from langchain.tools.base import BaseTool

from ollama import Client

# from splunklib import client
# from splunklib import results
# import splunklib

import requests
requests.packages.urllib3.disable_warnings() 
import time
import json

import os
import random
# import datetime
import sys # only for readin argv

class splunk_tool:
    def __init__(self, llm_url=os.getenv('LLM_URL') ,splunk_host=os.getenv('SPLUNK_HOST'), splunk_port=os.getenv('SPLUNK_PORT'), splunk_user=os.getenv('SPLUNK_USER'), splunk_pass=os.getenv('SPLUNK_PASS')):
        self.llm_url = llm_url
        self.splunk_host = splunk_host
        self.splunk_port = splunk_port
        self.splunk_user = splunk_user
        self.splunk_pass = splunk_pass
        
        print("mapping the envirnoment..")
        # self.env_map = self.map_env()
        self.env_map = '''
            {'sourcetypes': '[{"sourcetype": "PerfmonMk:Process"}, {"sourcetype": "Script:GetEndpointInfo"}, {"sourcetype": "Script:InstalledApps"}, {"sourcetype": "Script:ListeningPorts"}, {"sourcetype": "Unix:ListeningPorts"}, {"sourcetype": "Unix:SSHDConfig"}, {"sourcetype": "Unix:Service"}, {"sourcetype": "Unix:Update"}, {"sourcetype": "Unix:Uptime"}, {"sourcetype": "Unix:UserAccounts"}, {"sourcetype": "Unix:Version"}, {"sourcetype": "WinEventLog:Application"}, {"sourcetype": "WinEventLog:Microsoft-Windows-AppLocker/EXE and DLL"}, {"sourcetype": "WinEventLog:Microsoft-Windows-AppLocker/Packaged app-Execution"}, {"sourcetype": "WinEventLog:Microsoft-Windows-PowerShell/Operational"}, {"sourcetype": "WinEventLog:Security"}, {"sourcetype": "WinEventLog:System"}, {"sourcetype": "WinHostMon"}, {"sourcetype": "XmlWinEventLog:Microsoft-Windows-Sysmon/Operational"}, {"sourcetype": "access_combined"}, {"sourcetype": "alternatives"}, {"sourcetype": "amazon-ssm-agent"}, {"sourcetype": "amazon-ssm-agent-too_small"}, {"sourcetype": "apache_error"}, {"sourcetype": "aws:cloudtrail"}, {"sourcetype": "aws:cloudwatch"}, {"sourcetype": "aws:cloudwatch:guardduty"}, {"sourcetype": "aws:cloudwatchlogs"}, {"sourcetype": "aws:cloudwatchlogs:vpcflow"}, {"sourcetype": "aws:config:rule"}, {"sourcetype": "aws:description"}, {"sourcetype": "aws:elb:accesslogs"}, {"sourcetype": "aws:rds:audit"}, {"sourcetype": "aws:rds:error"}, {"sourcetype": "aws:s3:accesslogs"}, {"sourcetype": "bandwidth"}, {"sourcetype": "bash_history"}, {"sourcetype": "bootstrap"}, {"sourcetype": "cisco:asa"}, {"sourcetype": "cloud-init"}, {"sourcetype": "cloud-init-output"}, {"sourcetype": "code42:api"}, {"sourcetype": "code42:computer"}, {"sourcetype": "code42:org"}, {"sourcetype": "code42:security"}, {"sourcetype": "code42:user"}, {"sourcetype": "config_file"}, {"sourcetype": "cpu"}, {"sourcetype": "cron-too_small"}, {"sourcetype": "df"}, {"sourcetype": "dmesg"}, {"sourcetype": "dpkg"}, {"sourcetype": "error-too_small"}, {"sourcetype": "errors"}, {"sourcetype": "errors-too_small"}, {"sourcetype": "ess_content_importer"}, {"sourcetype": "hardware"}, {"sourcetype": "history-2"}, {"sourcetype": "interfaces"}, {"sourcetype": "iostat"}, {"sourcetype": "lastlog"}, {"sourcetype": "linux_audit"}, {"sourcetype": "linux_secure"}, {"sourcetype": "localhost-5"}, {"sourcetype": "lsof"}, {"sourcetype": "maillog-too_small"}, {"sourcetype": "ms:aad:audit"}, {"sourcetype": "ms:aad:signin"}, {"sourcetype": "ms:o365:management"}, {"sourcetype": "ms:o365:reporting:messagetrace"}, {"sourcetype": "netstat"}, {"sourcetype": "o365:management:activity"}, {"sourcetype": "openPorts"}, {"sourcetype": "osquery:info"}, {"sourcetype": "osquery:results"}, {"sourcetype": "osquery:warning"}, {"sourcetype": "out-3"}, {"sourcetype": "package"}, {"sourcetype": "protocol"}, {"sourcetype": "ps"}, {"sourcetype": "stream:arp"}, {"sourcetype": "stream:dhcp"}, {"sourcetype": "stream:dns"}, {"sourcetype": "stream:http"}, {"sourcetype": "stream:icmp"}, {"sourcetype": "stream:igmp"}, {"sourcetype": "stream:ip"}, {"sourcetype": "stream:mysql"}, {"sourcetype": "stream:smb"}, {"sourcetype": "stream:smtp"}, {"sourcetype": "stream:tcp"}, {"sourcetype": "stream:udp"}, {"sourcetype": "symantec:ep:agent:file"}, {"sourcetype": "symantec:ep:agt_system:file"}, {"sourcetype": "symantec:ep:behavior:file"}, {"sourcetype": "symantec:ep:packet:file"}, {"sourcetype": "symantec:ep:risk:file"}, {"sourcetype": "symantec:ep:scm_system:file"}, {"sourcetype": "symantec:ep:security:file"}, {"sourcetype": "symantec:ep:traffic:file"}, {"sourcetype": "syslog"}, {"sourcetype": "time"}, {"sourcetype": "top"}, {"sourcetype": "usersWithLoginPrivs"}, {"sourcetype": "vmstat"}, {"sourcetype": "who"}, {"sourcetype": "yum-too_small"}]'}
            '''

    def generate_spl(self, user_input):
        client = Client(host=self.llm_url)
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

        response = client.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': instructions + "\nuser input:" + user_input
        },
        ])

        spl=response['message']['content']
  
        return spl
    
    def map_env(self):
        # Method to map the Splunk envirnoment 
        env_map = {}
        spl = "index!=_* |stats count by sourcetype |table sourcetype"
        env_map['sourcetypes'] = self.run_search(spl)
        return env_map

    def run_search(self, spl):
        
        search_command = "search " + spl
        scheme = 'https'
        host = self.splunk_host + ":" + self.splunk_port
        username = self.splunk_user
        password = self.splunk_pass
        unique_id  = random.randint(10000000,99999999)
        post_data = { 'id' : unique_id,
                    'search' : search_command,
                    'earliest_time' : '1',
                    'latest_time' : 'now',
                    }
        splunk_search_base_url = scheme + '://' + host + '/servicesNS/' + username + '/search/search/jobs'
        resp = requests.post(splunk_search_base_url, data = post_data, verify = False, auth = (username, password))

        # print(resp.text)

        is_job_completed = ''

        while(is_job_completed != 'DONE'):
            time.sleep(5)
            get_data = {'output_mode' : 'json'}
            job_status_base_url = scheme + '://' + host + '/servicesNS/{}/search/search/jobs/{}'.format(username, unique_id)
            resp_job_status = requests.post(job_status_base_url, data = get_data, verify = False, auth = (username, password))
            print(resp_job_status)
            resp_job_status_data = resp_job_status.json()
            is_job_completed = resp_job_status_data['entry'][0]['content']['dispatchState']
            print("Current job status is {}".format(is_job_completed))

        splunk_summary_base_url = scheme + '://' + host + '/servicesNS/{}/search/search/jobs/{}/results?count=0'.format(username, unique_id)
        splunk_summary_results = requests.get(splunk_summary_base_url, data = get_data, verify = False, auth = (username, password))
        splunk_summary_data = splunk_summary_results.json()

        # #Print the results in python format (strings will be in single quotes)
        # for data in splunk_summary_data['results']:
        #     print(data)
        # print(splunk_summary_results.status_code)
        # print(splunk_summary_results.raise_for_status())
        # print(json.dumps(splunk_summary_data))
        # print(json.dumps(splunk_summary_data['results']))
        return json.dumps(splunk_summary_data['results'])
    
    # def analyze_search_results(self, results):

    #     client = Client(host=self.llm_url)
    #     instructions = f'''
    #     Your Job is to help security analysts by reading this JSON search results and draw conclusions to be saved as case notes for the investigation.
    #     You need to answer the following questions:
    #     - Are there any users? what did they do?
    #     - Are there any IP addresses? tell me about them
    #     - Are there any actions taken?
    #     - Are there any known malicious commands
    #     - Do you see anything suspecious?
    #     Results:
        
    #     '''
    #     response = client.chat(model='llama3', messages=[
    #     {
    #         'role': 'user',
    #         'content': instructions + results
    #     },
    #     ])

    #     analysis=response['message']['content'] 
    #     return analysis

    def answer_user_question(self, question, search_results):

        client = Client(host=self.llm_url)
        instructions = f'''
        Your Job is to read the User Question and the Search Results, then answer the User Question based on the search results.
        Instructions:
        - Keep your answers short and straight to the point.
        - If you do not understand the question, summerize the search results.
        - If search results is emply, just say "No search data was returned".
        '''
        response = client.chat(model='llama3', messages=[
        {
            'role': 'user',
            'content': instructions + "\nUser Question: " + question + "\nSearch Results:\n" + search_results
        },
        ])

        analysis=response['message']['content'] 
        return analysis  

class splunk_search(BaseTool):
    name = "splunk_search"
    description = (
        "You can use this to search data in splunk"
    )

    def _run(self, query: str) -> str:
        s = splunk_tool()
        spl = s.generate_spl(query)
        s.run_search(spl)

        return "response"

    async def _arun(self, query: str) -> str:
        """Use the Cloudwatch tool asynchronously."""
        raise NotImplementedError("Cloudwatch tool does not support async")


user_question = sys.argv[1]

s = splunk_tool()
print("Generating SPL..")
spl = s.generate_spl(user_question)
print("### SPL TO BE USED:")
print(spl)
print("Running search..")
search_results = s.run_search(spl)
print("\n###SEARCH RESULTS:")
print(search_results)
# analysis = s.analyze_search_results(search_results)
# print("\n[ANALYSIS:]")
# print(analysis)
print("Analysing search results..")
answer = s.answer_user_question(user_question, search_results)
print("\n###Ansswer:")
print(answer)

