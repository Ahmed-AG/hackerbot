from hb_engine import hb_engine

from colorama import Fore, Back, Style
import sys

class hb():
    def print_banner(self):
        print("Welcome to " + Fore.GREEN + "HackerBot" + Style.RESET_ALL + "!")

    def process_user_input(self,user_input):
        subroutine = user_input.split(' ')[0]
        if subroutine == "exit":
            print("Good Bye!")
            exit()

        else:
            hb_langchain.request()
            # ai_response, exe = langchain_hb.ask_ai(user_input, self.index, self.exe)
            # if self.stats == True:
            #     self.submit_stats(user_input, ai_response['answer'],ai_response['sources'])

    def prompt(self,):
        user_input = input(Fore.GREEN + "hb>" + Style.RESET_ALL)
        self.process_user_input(user_input)

    def run(self,):
        self.print_banner()
        while(True):
            self.prompt()

if __name__ == "__main__":
    hb = hb()
    if len(sys.argv) > 1:
        if sys.argv[1] == "--stats-off":
            hb.stats = False
    hb.run()