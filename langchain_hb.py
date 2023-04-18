import json
from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.document_loaders import DirectoryLoader
from colorama import Fore, Back, Style
            
def initialize_index():
    index = initialize_index()
    return index

def ask_ai(user_input, index, exe):
    # prompt = "Answer only with the actual command. {}".format(user_input)
    prompt = "Answer only with the actual HCL code. {}".format(user_input)
    ai_response = index.query_with_sources(prompt)
   
    exe["command"] = ai_response['answer'][:-1]
    exe["type"] = "AI"

    print("Skills: {}".format(ai_response['sources']))
    print("Execute:" + Fore.GREEN + "{}".format(exe["command"]) + Style.RESET_ALL + "\n Type \'go\' to execute:")

    return ai_response, exe

def initialize_index():
    loader = DirectoryLoader('/home/aag/repos/terraform-provider-aws/website/docs/r/', glob="*.markdown", loader_cls=TextLoader)
    # loader = DirectoryLoader('skills/', glob="*.skill", loader_cls=TextLoader)
    index = VectorstoreIndexCreator().from_loaders([loader])
    docs = loader.load()
    # for doc in docs:
    #     print(doc['source'])
    print("number of skills loaded: {}".format(len(docs)))
    return index