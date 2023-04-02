import os
import openai

def get_openAIKey():
    return os.environ["OPENAI_KEY"]

def read_file(file_path):
    file = open(file_path, "r")
    return file.readlines()

def talk_to_ai(prompt):
    openai.api_key = get_openAIKey()
    response = openai.Completion.create(
        model="text-davinci-003",
        # stop="###",
        prompt=prompt,
        temperature=0,
        max_tokens=250,
    )
    return response['choices'][0]['text']

def excute_command(command, output_file):
    os.system("{} | tee {}".format(command, output_file))
    command_output = read_file(output_file)
    return command_output
