# hackerBot
An AI-CyberSecurity Bot Based on OpenAI's Models. hackerbot is being trained to do various Cyber Security tasks

## Skills
Skill | Tools | Status |
--- | --- | ---
aws cli | aws cli | Beta
Port Scanning | nmap | Beta
Netcat | nc | Beta
Reading AWS logs | Using LangChain Agent and AWS CloudWatch tool (CWTOOL) | Beta

## Set up
- Clone the repo
```
git clone https://github.com/Ahmed-AG/hackerbot.git
```
- Install prerequisites 
```
pip install openai
pip install langchain
pip install chromadb
pip install google-search-results
pip install boto3
pip install tiktoken
```
- Export OpenAI Key
```
export OPENAI_API_KEY=<YOUR_OPENAI_KEY>
export SERPAPI_API_KEY=<SERAPI_KEY>
export CWTOOL_LOG_GROUPS=<LOGGROUP1,LOGGROUP2>
export CWTOOL_REGION=<AWS REGION>
```

## Usage
hackerBot will examine the first word of the user's input. if it is one of the following commands, it will execute the corresponding action. Otherwise, it will use user's input as part of the prompt to the AI model to generate the proper command needed.
Command | Description | Use Example
--- | --- | ---
agent | starts custom LangChain Agent | agent use cloudwatch to search for..
go | Executes the command last generated. Used as a human verification step | go
cmd | Executes custom commands directly (no AI) | cmd ls -l
reload | Reloads skills from files | reload
exit | Exits hackerbot | exit

## Examples
### Search CloudWatch Logs
```
python hb.py
hb>agent use cloudwatch to find out the IP addresses used by admin
```
![alt text](images/agent-cwtool.png?raw=true)


### Showing instances

```
python hb.py
hb>show me instances in us-east-2. display instance ID, instance name, and AMi in a table
```

![alt text](images/describe-instances.png?raw=true)

### Scanning an IP address

```
python hb.py
hb>scan 8.8.8.8 for ports less than 1000 and run services scan
```

![alt text](images/port-scan-screenshot.png?raw=true)


### Run commands directly (no AI)

```
$ python hb.py
hb>cmd python --version
Python 3.10.8
```
## Support
To report a bug, request a feature, or submit a suggestion/feedback, please submit an issue through the GitHub repository: https://github.com/Ahmed-AG/hackerbot/issues/new

## Privacy Disclaimer
By default, hackerBot logs the human requests as well as the AI generated responses to a remote location. This is to enhance the skills.
If you want to disable this feature run hackerBot with `--stats-off`

```
python hb.py --stats-off
```
