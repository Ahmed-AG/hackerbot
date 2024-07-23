import argparse

from .version import __version__
from .tools import Splunk, SplunkRequest
from .logging import (
    logger,
    set_level,
)
from .exceptions import (
    GenerationError,
)


def run_splunk(args: argparse.Namespace) -> None:
    llm = get_llm(args)
    splunk = Splunk(
        llm_model=llm,
    )

    try:
        response = splunk.run(SplunkRequest(question=args.question, return_spl=args.print_spl))
    except GenerationError as e:
        logger.error(f"Error running Splunk tool: {e}")
        print("Could not generate a response. Please check your LLM configuration.")
        exit(1)
    except Exception as e:
        logger.error(f"Error running Splunk tool: {e}")
        print("Error running Splunk tool. Please try again later.")
        exit(1)

    if args.print_spl:
        print(f"\n\nSPL Query: '{response.spl}'")

    print("\n\nAnswer:\n\n")
    print(response.answer)

def get_llm(argparser: argparse.Namespace) -> str:
    if argparser.use_llama3:
        return "llama3"
    elif argparser.use_llama3_1:
        return "llama3.1"
    else:
        return "llama3"

def add_splunk_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "question",
        help="The question to ask Splunk",
    )
    parser.add_argument(
        "--print-spl",
        action="store_true",
        default=False,
        help="Print the SPL query",
    )

subcommands = {
    "splunk": run_splunk,
}


def main() -> None:
    argparser = argparse.ArgumentParser(
        prog="Hackerbot",
        description="Hackerbot"
    )
    splunk_parser = argparser.add_subparsers(
        title="Subcommands",
        dest="subcommand",
    )

    add_splunk_arguments(splunk_parser.add_parser(
        "splunk",
        help="Search for data in Splunk",
    ))


    llm_arg_group = argparser.add_argument_group(
        "Large Language Model (LLM)"
    )

    llm_type_group = llm_arg_group.add_mutually_exclusive_group()
    llm_type_group.add_argument(
        "--use-llama3",
        action="store_true",
        default=True,
        help="Use the llama3 model",
    )
    llm_type_group.add_argument(
        "--use-llama3.1",
        action="store_true",
        default=False,
        help="Use the llama3.1 model",
    )

    logging_arg_group = argparser.add_argument_group(
        "logging"
    )
    logging_arg_group.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug logging",
    )

    argparser.add_argument('--version', '-V', action='version', version=f'%(prog)s v{__version__}')

    args = argparser.parse_args()

    if args.debug:
        set_level("DEBUG")

    try:
        subcommands[args.subcommand](args)
    except KeyError:
        argparser.print_help()
        exit(1)
