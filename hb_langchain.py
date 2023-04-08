import json
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import DirectoryLoader

def initialize_index():
    loader = DirectoryLoader('skills/', glob="*.skill", loader_cls=TextLoader)
    index = VectorstoreIndexCreator().from_loaders([loader])
    docs = loader.load()
    # for doc in docs:
    #     print(doc['source'])
    print("number of skills loaded: {}".format(len(docs)))
    return index