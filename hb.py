import common

exe = {
    "command" : "",
    "type": ""
}

def print_banner():
    print("Welcome to HackerBot!")

def answer_user_questions(question):
    data = common.read_file("scan.out")
    context = "based on this:\n{}".format(data)
    prompt = "{}\n{} ->".format(str(context), question)
    return common.talk_to_ai(prompt)

def invoke_scanner(user_input):
    context_file = "contexts/port_scanning.txt"
    # output_file = "scanner.out"
    context = common.read_file(context_file)
    prompt = "{}\n{} ->".format(str(context), user_input)

    exe["command"] = common.talk_to_ai(prompt)
    exe["type"] = "scan"

    print("Command to execute: {}".format(exe["command"]))
    print("Type \'exec\' to execute")

def process_user_input(user_input):
    subroutine = user_input.split(' ')[0]
    if subroutine == "scan":
        invoke_scanner(user_input)
    elif subroutine == "exec":
        common.excute_command(exe["command"],"{}.out".format(exe["type"]))
    elif subroutine == "question":
        print(answer_user_questions(user_input))
    elif subroutine == "exit":
        print("Good Bye!")
        exit()

def prompt():
    user_input = input("hb>")
    process_user_input(user_input)

def hb():
    print_banner()
    while(True):
        prompt()

if __name__ == "__main__":
    hb()




