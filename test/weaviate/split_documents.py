import re
import json

def split_documents(SOURCE_DOCUMENTS,chunk_size , overlap_size):
    data_json = []
    for document in SOURCE_DOCUMENTS:
        file = open(document)
        content = file.read()
        file.close()

        source_text = re.sub(r"\s+", " ", content)  # Remove multiple whitespaces
        text_words = re.split(r"\s", source_text)  # Split text by single whitespace

        chunks = []
        for i in range(0, len(text_words), chunk_size):  # Iterate through & chunk data
            chunk = " ".join(text_words[max(i - overlap_size, 0): i + chunk_size])  # Join a set of words into a string
            chunks.append(chunk)

        # loop over the chunks to create the JSON file
        for index, chunk_item in enumerate(chunks):
            chunk_json = {
                    "title": document + " - " + str(index),
                    "data": chunk_item,
                    "source": document
                }
            data_json.append(chunk_json)
    return data_json

# Main Driver Example
# chunk_size = 300
# overlap_size = 25
# SOURCE_DOCUMENTS = [
#     "data/nmap.man",
#     "data/nc.man"
# ]
# split_documents_data = split_documents(SOURCE_DOCUMENTS,chunk_size , overlap_size)
# print(split_documents_data)
