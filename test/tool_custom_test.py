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

    def _read_logs(self, account_secrets, query, log_group_names, human_request):
        insights_client = boto3.client('logs',region_name = 'us-east-2')
        
        current_epoch_time = int(time.time())
        subtraction_amount = timedelta(days=self.CWTOOL_DAYS_TO_SEARCH)
        new_epoch_time = current_epoch_time - int(subtraction_amount.total_seconds())

        # try:

        start_query_response = insights_client.start_query(
            # logGroupNames=[
            #     'cloudtrail',
            #     'vpcflow'
            #     ],
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
        # except:
        #     print("Error in read_logs()")
        #     response = {
        #         "statistics" : {"recordsMatched" : "Error in read_logs()" }
        #     }
        #     response['statistics']['recordsMatched']
        #     # handle_cloudwatch_error(response,human_request, query)
        return response

    def _check_settings(self):
        if os.getenv('CWTOOL_DAYS_TO_SEARCH') != None:
            self.CWTOOL_DAYS_TO_SEARCH = os.getenv('CWTOOL_DAYS_TO_SEARCH')

        if os.getenv('CWTOOL_LLM_MODEL') != None:
            self.CWTOOL_LLM_MODEL = os.getenv('CWTOOL_LLM_MODEL')
        
        if os.getenv('CWTOOL_LOG_GROUPS') != None:
            groups = os.getenv('CWTOOL_LOG_GROUPS')
            self.CWTOOL_LOG_GROUPS = [group.strip() for group in groups.split(',')]

        # print(self.CWTOOL_LLM_MODEL)
        # print(self.CWTOOL_LOG_GROUPS)
        # print(self.CWTOOL_DAYS_TO_SEARCH)

    def _run(self, query: str) -> str:
        """Run Cloudwatch queries."""

        self._check_settings()

        print("\nCloudwatch Tool - Request:")
        print(" " + Fore.GREEN + query + Style.RESET_ALL)

        cloudwatchinsight_Query = self.get_query_chat(query, self.CWTOOL_LLM_MODEL)
        print("Cloudwatch Tool - Generated Query:")
        print(" " + Fore.GREEN + cloudwatchinsight_Query + Style.RESET_ALL)

        response = self._read_logs("account_secrets", cloudwatchinsight_Query, self.CWTOOL_LOG_GROUPS, "human_request")
        print("Cloudwatch Tool - Response:")
        print(" " + Fore.GREEN + str(response) + Style.RESET_ALL)

        return response

    async def _arun(self, query: str) -> str:
        """Use the Cloudwatch tool asynchronously."""
        raise NotImplementedError("Cloudwatch tool does not support async")

# Test Driver:
# cw = CloudWatchInsightQuery()
# print(cw.run("fields @message | limit 1"))

