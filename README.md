# hackerBot
An AI-CyberSecurity Bot Based on OpenAI's Models. hackerbot is being trained to do various Cyber Security tasks

## Skills
Skill | Tools | Status |
--- | --- | ---
aws cli | aws cli | Beta
Port Scanning | nmap | Beta
Netcat | nc | Beta
Reading AWS logs | AWS CloudWatch Insight | Coming soon

## Usage
hackerbot will use the first "word" in your promopt to decide the action it needs to take. The following are the currently supported actions:
Actions | Details
--- | ---|
exit | Exits hackerbot 
go | Executes the command last generated
reload | Reloads skills from files

## Example

Scanning an IP address:

```
python hb.py
hb>scan 8.8.8.8 for ports less than 1000 and run services scan
```

![alt text](hackerbot-screenshot-1.png?raw=true)

