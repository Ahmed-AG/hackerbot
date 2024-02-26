# Reference: https://weaviate.io/developers/weaviate/quickstart
import weaviate
import json
import sys
import os
import openai

# Testing Parameters:
QUESTION = sys.argv[1]
OPENAI_APIKEY = os.environ['OPENAI_APIKEY']
CLASS_NAME = "Man_pages"
NUMBER_OF_RESULTS_TO_RETURN = 5

# Connect to Weaviate DB
client = weaviate.Client(
    url = "http://localhost:8080",
    additional_headers = {
        "X-OpenAI-Api-Key": OPENAI_APIKEY
    }
)

response = (
    client.query
    .get(CLASS_NAME, ["title", "data", "source"])
    .with_near_text({"concepts": QUESTION})
    .with_limit(NUMBER_OF_RESULTS_TO_RETURN)
    .do()
)
data = response['data']['Get'][CLASS_NAME]

# Send request to OpenAI
OPENAI_APIKEY = os.environ['OPENAI_APIKEY']
openai.api_key = OPENAI_APIKEY
prompt = "Answer only with the actual command that gets the job done. Nothing else. Only asnwer based of the following: " + str(data)
completions = openai.chat.completions.create(
    model="gpt-3.5-turbo",
    stop="###",
    temperature=0,
    max_tokens=250,
    messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": QUESTION}
        ]
    )

print("Command:")
print(completions.choices[0].message.content)
