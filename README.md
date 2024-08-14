# HackerBot
An AI-CyberSecurity Bot. HackerBot is being trained to help investigate security incidents. We started by teaching HackerBot how to use [Splunk](https://www.splunk.com/).

## prerequisites
#### 1. Ollama
Ollama is used to host [Llama 3.1](https://ai.meta.com/blog/meta-llama-3-1/) (and other models) locally. Download and run [Ollama here](https://ollama.com/).
#### 2. Splunk Instance
HackerBot helps security analysts by searching data in Splunk. You will need an accessible instance Splunk instance.

## Use Hackerbot

#### 1. Install Hackerbot
```bash
pip install hackerbot
```

#### 2. Configure Hackerbot
```bash
hackerbot_cli.py configure
```
#### 3. Run Hackerbot
```bash
hackerbot_cli.py splunk "show me http and https network traffic going to 8.8.8.8"
```
