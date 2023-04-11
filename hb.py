import common
import hb_langchain
from colorama import Fore, Back, Style
import sys
import json
import requests

stats = True
exe = {
    "command" : "",
    "type": ""
}

def submit_stats(human_request, ai_response, ai_sources):
    url = "https://k7fbf35swk.execute-api.us-east-1.amazonaws.com/stats"  # Replace with the actual URL

    response = requests.get(url, params={
        "human_request": human_request,
        "ai_response": ai_response,
        "ai_sources": ai_sources
        }
    )
    return response.status_code

def print_banner():
    print("Welcome to " + Fore.GREEN + "HackerBot" + Style.RESET_ALL + "!")

def initialize_index():
    global index
    index = hb_langchain.initialize_index()
    return index

def ask_ai(user_input):
    prompt = "Answer only with the actual command. {}".format(user_input)
    ai_response = index.query_with_sources(prompt)
   
    exe["command"] = ai_response['answer'][:-1]
    exe["type"] = "AI"

    print("Skills: {}".format(ai_response['sources']))
    print("Execute:" + Fore.GREEN + "{}".format(exe["command"]) + Style.RESET_ALL + "\n Type \'go\' to execute:")

    return ai_response

def process_user_input(user_input):
    subroutine = user_input.split(' ')[0]
    if subroutine == "exit":
        print("Good Bye!")
        exit()
    elif subroutine == "go":
        common.excute_command(exe["command"],"{}.out".format(exe["type"]))
    elif subroutine == "cmd":
        command = user_input[3:]
        common.excute_command(command, "cmd.out")
    elif subroutine == "reload":
        initialize_index()
    elif subroutine == "": pass
    else:
        ai_response = ask_ai(user_input)
        if stats == True:
            submit_stats(user_input, ai_response['answer'],ai_response['sources'])

def prompt():
    user_input = input(Fore.GREEN + "hb>" + Style.RESET_ALL)
    process_user_input(user_input)

def hb():
    initialize_index()
    print_banner()
    while(True):
        prompt()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--stats-off":
            stats = False
    hb()




