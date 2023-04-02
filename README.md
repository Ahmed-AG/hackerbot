# hackerbot - POC
An AI-CyberSecurity Bot Based on OpenAI's Models. hackerbot is being trained to do various cybr security tasks

## Skills
Skill | Tools | Status |
--- | --- | ---
Port Scanning | nmap | In progress
Reading logs | AWS CloudWatch Insight | Coming soon

## Usage
hackerbot will use the first "word" in your promopt to decide the action it needs to take. The following are the currently supported actions:
Actions | Details
--- | ---|
scan | Runs a port scan
exit | Exits hackerbot 

## Example

```
hb>scan 8.8.8.8 for ports less than 1000 and run services scan
```

![alt text](hackerbot-screenshot-1.png?raw=true)

