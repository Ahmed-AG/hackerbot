from typing import Callable
from pydantic import Field
from langchain.tools.base import BaseTool
import boto3
import time
from datetime import datetime, timedelta
import os
import openai
from colorama import Fore, Back, Style

class CloudWatchInsightQuery(BaseTool):
    """Tool that adds the capability to search AWS Cloudwatch for input."""

    # Default config
    CWTOOL_LLM_MODEL = "gpt-4"
    CWTOOL_LOG_GROUPS = []
    CWTOOL_DAYS_TO_SEARCH = 30
    CWTOOL_REGION = "us-east-1"

    name = "cloudwatchquery"
    description = (
        "You can use this to run AWS Cloudwwatch insights query to query logs"
    )

    def get_openAIKey(self):
        key = 'OPENAI_API_KEY'
        return os.getenv(key)

    def read_file(self, file_path):
        file = open(file_path, "r")
        return file.readlines()

    def generate_prompt(self, human_request):
        training_set = self.read_file("test/aws-cloudwatch-insight-query.man")
        prompt = "consider this:" + str(training_set) + "\n" + human_request + "->"
        return prompt

    def get_query_chat(self, human_request, model):
        openai.api_key = self.get_openAIKey()
        prompt = self.generate_prompt(human_request)
        response = openai.ChatCompletion.create(
            model=model,
            # model="gpt-4",
            stop="###",
            temperature=0,
            max_tokens=250,
            messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": human_request}
                ]
            )
        return response['choices'][0]['message']['content']

    def _read_logs(self, account_secrets, query, log_group_names, human_request, region):

        # Set time 
        current_epoch_time = int(time.time())
        subtraction_amount = timedelta(days=self.CWTOOL_DAYS_TO_SEARCH)
        new_epoch_time = current_epoch_time - int(subtraction_amount.total_seconds())

        insights_client = boto3.client('logs',region_name = region)
        try:

            start_query_response = insights_client.start_query(
                logGroupNames=log_group_names,
                startTime=new_epoch_time,
                endTime=current_epoch_time,
                queryString=query,
            )
            while(1):
                time.sleep(2)
                response = insights_client.get_query_results(
                    queryId=start_query_response['queryId']
                    )
                print("Cloudwatch Search: " + response['status'])
                if (response['status'] == "Complete"):
                    break
        except:
            print("Error in read_logs()")
            response = {
                "statistics" : {"recordsMatched" : "Error in read_logs()" }
            }
            response['statistics']['recordsMatched']
        return response

    def _check_settings(self):
        if os.getenv('CWTOOL_DAYS_TO_SEARCH') != None:
            self.CWTOOL_DAYS_TO_SEARCH = os.getenv('CWTOOL_DAYS_TO_SEARCH')

        if os.getenv('CWTOOL_REGION') != None:
            self.CWTOOL_REGION = os.getenv('CWTOOL_REGION')

        if os.getenv('CWTOOL_LLM_MODEL') != None:
            self.CWTOOL_LLM_MODEL = os.getenv('CWTOOL_LLM_MODEL')
        
        if os.getenv('CWTOOL_LOG_GROUPS') != None:
            groups = os.getenv('CWTOOL_LOG_GROUPS')
            self.CWTOOL_LOG_GROUPS = [group.strip() for group in groups.split(',')]
        else:
            groups = input("CW_Tool: You need to set log group names. use comma seperated values:\n")
            self.CWTOOL_LOG_GROUPS = [group.strip() for group in groups.split(',')]

        print("\nCW_Tool's settings:")
        print(" CWTOOL_LLM_MODEL=" + self.CWTOOL_LLM_MODEL)
        print(" CWTOOL_LOG_GROUPS=" + str(self.CWTOOL_LOG_GROUPS))
        print(" CWTOOL_DAYS_TO_SEARCH=" + str(self.CWTOOL_DAYS_TO_SEARCH))
        print(" CWTOOL_REGION=" + self.CWTOOL_REGION)

    def _run(self, query: str) -> str:
        """Run Cloudwatch queries."""

        self._check_settings()

        print("\nCloudwatch Tool - Request:")
        print(" " + Fore.GREEN + query + Style.RESET_ALL)

        cloudwatchinsight_Query = self.get_query_chat(query, self.CWTOOL_LLM_MODEL)
        print("Cloudwatch Tool - Generated Query:")
        print(" " + Fore.GREEN + cloudwatchinsight_Query + Style.RESET_ALL)

        # TODO: add support for STS AssumeRole
        response = self._read_logs("TODO_account_secrets", cloudwatchinsight_Query, self.CWTOOL_LOG_GROUPS, "legacy_human_request", self.CWTOOL_REGION)
        print("Cloudwatch Tool - Response:")
        print(" " + Fore.GREEN + str(response) + Style.RESET_ALL)

        return response

    async def _arun(self, query: str) -> str:
        """Use the Cloudwatch tool asynchronously."""
        raise NotImplementedError("Cloudwatch tool does not support async")

