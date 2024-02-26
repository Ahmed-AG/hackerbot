# Testing Weaviate
## Introduction
Weaviate is an open source, AI-native vector database that helps
developers create intuitive and reliable AI-powered applications.

Weaviate instance can be hosted in their cloud or run locally on docker or K8s. For this test, we are using docker-compose to host an instance.

## Workflow:
1. Create Weaviate DB Instance
2. Upload data into the Weaviate Instance
   1. Chop a document into partitions
   2. Upload partitions into the Weaviate instance
3. Query the data:
   1. Use embedded models to get a list of relevant partition 
   2. use OpenAI chat or completion models to get the actual answer

## Testing Weaviate

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Set `OPENAI_APIKEY`
```bash
export OPENAI_APIKEY=XXXXXX
```

3. Run the weaviate instance locally 
```bash
cd  cd test/weaviate/docker/
docker compose up -d
docker ps
cd ..
```
Test Weaviate by going to `http://localhost:8080/`

4. Once Weaviate is running, update/create data by running:
```bash
cd tests
python3 weaviate-create.py 
```

5. Test LLM Query:
```bash
cd tests
python3 weaviate-query.py <YOUR QUESTION> 
```

## Examples:
```bash
% python3 weaviate-query.py "scan subnet 192.168.5.0/16"
Command:
nmap 192.168.5.0/16
```

```bash
% python3 weaviate-query.py "scan subnet 192.168.5.200 and use all options"
Command:
nmap -A 192.168.5.200
```

```bash
% python3 weaviate-query.py "scan subnet 192.168.5.200 and -A"
Command:
nmap 192.168.5.200 -A
```

```bash
% python3 weaviate-query.py "scan subnet 192.168.5.0/16  and http and https ports but also show why the ports are open or closed "
Command:
nmap -sS -p 80,443 --reason 192.168.5.0/16
```

```bash
% python3 weaviate-query.py "open a port 555 for listening"
Command:
nc -l -p 555
```

```bash
% python3 weaviate-query.py "create a shell listening on port 5555"
Command:
nc -l -p 5555
```

```bash
% python3 weaviate-query.py "create a shell listening on port 5555. I need this to execute a shell upon connecting"
Command:
nc -l -p 5555 -e /bin/sh
```

```bash
% python3 weaviate-query.py "connect to host 192.168.1.5 on port 5555"
Command:
nc 192.168.1.5 5555
```