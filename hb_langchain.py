import json
# from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import DirectoryLoader

def initialize_index():
    loader = DirectoryLoader('documents/', glob="*.inst", loader_cls=TextLoader)
    index = VectorstoreIndexCreator().from_loaders([loader])
    docs = loader.load()
    # for doc in docs:
    #     print(doc['source'])
    print("number of documents loaded: {}".format(len(docs)))
    return index

def ask_ai(user_input,index):
    return index.query_with_sources(user_input)

# query = "Answer only with the actual command. Do not add \n. what instances do I have in us east 1? use jq to extract only the instance ids and amis in a table. use region us-east-2 and profile msslab"

# print(json.dumps(index.query_with_sources(query), indent=2))
