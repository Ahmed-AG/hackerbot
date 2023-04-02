import json
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import DirectoryLoader

loader = TextLoader('local/nmap.man')
# loader = DirectoryLoader('local/', glob="*.*")
index = VectorstoreIndexCreator().from_loaders([loader])

query = "Answer only with the actual command. Do not add \n. scan 192.168.5.200 for open ports less than 1000 with verbose ->"
# index.query(query)

print(json.dumps(index.query_with_sources(query), indent=2))
# print(index.query(query))


# embeddings = OpenAIEmbeddings(model_name="ada")
# text = "This is a test document."
# query_result = embeddings.embed_query(text)
# doc_result = embeddings.embed_documents([text])

# print(doc_result)