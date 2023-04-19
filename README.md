# hackerBot
An AI-CyberSecurity Bot Based on OpenAI's Models. hackerbot is being trained to do various Cyber Security tasks.
You can either run hackerBot in a docker container (the fast option) or install it locally

## Skills
Skill | Tools | Status |
--- | --- | ---
aws cli | aws cli | Beta
Port Scanning | nmap | Beta
Netcat | nc | Beta
Reading AWS logs | Using LangChain Agent and AWS CloudWatch tool (CWTOOL) | Beta

## Run in Docker
The easiest way to run hackerBot is to run it inside a docker container. Set your secrets and run the command below:
```
sudo docker run -w /home/hb/hackerbot/ \
-e SERPAPI_API_KEY=<SERPAPI_API_KEY> \
-e OPENAI_API_KEY=<OPENAI_API_KEY> \
-e CWTOOL_LOG_GROUPS=cloudtrail,vpcflow \
-e CWTOOL_REGION=us-east-1 \
-ti ahmedag/hackerbot python hb.py
```
Dockerfile is at `docker/Dockerfile`

## Manual Setup
Instead of using the docker image, you can set your own environment.

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
- Set environment variables 
```
export OPENAI_API_KEY=<YOUR_OPENAI_KEY>
export SERPAPI_API_KEY=<SERAPI_KEY>
export CWTOOL_LOG_GROUPS=<LOGGROUP1,LOGGROUP2>
export CWTOOL_REGION=<AWS REGION>
```

## Use
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
