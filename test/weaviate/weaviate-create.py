# Reference: https://weaviate.io/developers/weaviate/quickstart
import weaviate
import json
import os
import requests
import codecs
from split_documents import split_documents as sd

# Testing Parameters:
OPENAI_APIKEY = os.environ['OPENAI_APIKEY']
CLASS_NAME = "Man_pages"
CHUNK_SIZE = 300
OVERLAP_SIZE = 25
SOURCE_DOCUMENTS = [
    "data/nmap.man",
    "data/nc.man"
]

# Connect to Weaviate DB
client = weaviate.Client(
    url = "http://localhost:8080",  
    # auth_client_secret=weaviate.auth.AuthApiKey(api_key="YOUR-WEAVIATE-API-KEY"),  # Replace w/ your Weaviate instance API key
    additional_headers = {
        "X-OpenAI-Api-Key": OPENAI_APIKEY  
    }
)

class_obj = {
    "class": CLASS_NAME,
    "vectorizer": "text2vec-openai",  
    "moduleConfig": {
        "text2vec-openai": {},
        "generative-openai": {}
    }
}

# Check Class exists
schema = client.schema.get()
CLASS_EXISTS = False
for class_name in schema['classes']:
    print(CLASS_NAME)
    print(class_name['class'])
    if class_name['class'] == CLASS_NAME:
        CLASS_EXISTS = True
        break

# Create class
if (CLASS_EXISTS == True):
    print("Class esists!")
else:
    client.schema.create_class(class_obj)
    print("Class Created!")

split_documents_data = sd(SOURCE_DOCUMENTS,CHUNK_SIZE , OVERLAP_SIZE)
# print(split_documents_data)

client.batch.configure(batch_size=100)
with client.batch as batch:
    for i, d in enumerate(split_documents_data):
        print(f"importing Data: {i+1}: {d['title']}")

        properties = {
            "title": d["title"],
            "data": d["data"],
            "source": d["source"],
        }
        batch.add_data_object(
            data_object=properties,
            class_name=CLASS_NAME
        )