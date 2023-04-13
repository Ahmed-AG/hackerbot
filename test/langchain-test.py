import json
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import DirectoryLoader

# loader = TextLoader('local/nmap.man')
loader = DirectoryLoader('local/', glob="*.man", loader_cls=TextLoader)
index = VectorstoreIndexCreator().from_loaders([loader])

docs = loader.load()
# for doc in docs:
#     print(doc['source'])
print("number of documents loaded: {}".format(len(docs)))


# query = "Answer only with the actual command. Do not add \n. scan 192.168.5.200 for open ports less than 1000 with verbose ->"
# query = "Answer only with the actual command. Do not add \n. using metasploit, show available exploits with a single command ->"
# query = "Answer only with the actual command. Do not add \n. search for AWS logs showing the network traffic going to 8.8.8.8"
# query = "Answer only with the actual command. Do not add \n. use netcat to listen for incoming connections on port 776 ->"
query = "Answer only with the actual command. Do not add \n. what instances do I have in us east 1? use jq to extract only the instance ids and amis in a table. use region us-east-2 and profile msslab"



# index.query(query)

print(json.dumps(index.query_with_sources(query), indent=2))
# print(index.query(query))


# embeddings = OpenAIEmbeddings(model_name="ada")
# text = "This is a test document."
# query_result = embeddings.embed_query(text)
# doc_result = embeddings.embed_documents([text])

# print(doc_result)