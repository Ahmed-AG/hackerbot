import argparse
import sys
from .version import __version__
from .tools import SplunkTool, SplunkRequest, SplunkToolConfig
from .logging import (
    logger,
    set_level,
)
from .exceptions import (
    GenerationError,
    QueryError,
)


def run_splunk(args: argparse.Namespace) -> None:
    llm = get_llm(args)

    config = SplunkToolConfig(
        llm_model=llm,
    )
    splunk = SplunkTool(
        config=config,
    )

    request = SplunkRequest(
        question=args.input,
        return_spl=args.print_spl,
    )

    try:
        if args.generate:
            response = splunk.generate_spl(question=args.input)
            print(f"\n\nSPL Query: '{response}'")

        elif args.query:
            response = splunk.run_search(spl=args.input)
            print(f"\n\nSearch Results:\n\n{response}")

        elif args.analyze:
            print(args.spl_query_results)
            if args.spl_query_results == "":
                print("SQL query results are required when only performing an analysis using -a/--analyze. Please provide the SQL query results using the --sql-query-results flag. Refer to the help (-h/--help) for more information.")
                exit(1)
            response = splunk.analyze_results(question=args.input, search_results=args.spl_query_results)
            print(f"\n\nAnalysis:\n\n{response}")
        else:
            response = splunk.run(request)
            if args.print_spl:
                print(f"\n\nSPL Query: '{response.spl}'")

            print("\n\nAnswer:\n\n")
            print(response.answer)
    except QueryError as e:
        logger.error(f"Error running Splunk tool: {e}")
        print("Could not query Splunk. Please check your LLM configuration.")
        exit(1)
    except GenerationError as e:
        logger.error(f"Error running Splunk tool: {e}")
        print("Could not generate a response. Please check your LLM configuration.")
        exit(1)
    except Exception as e:
        logger.error(f"Error running Splunk tool: {e}")
        print("Error running Splunk tool. Please try again later.")
        exit(1)

def get_llm(argparser: argparse.Namespace) -> str:
    if argparser.use_llama3:
        return "llama3"
    elif argparser.use_llama3_1:
        return "llama3.1"
    else:
        return "llama3"

def add_splunk_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "input",
        help="Input for the Splunk tool. This can be a question or an SPL query depending on the action specified",
    )

    parser.add_argument(
        "--print-spl",
        action="store_true",
        default=False,
        help="Print the SPL query",
    )
    parser.add_argument(
        "--spl-query-results",
        dest="spl_query_results",
        type=str,
        default="",
        help="SQL query results. Used with the -a/--analyze flag to supply the own SQL query results",
    )
    actions = parser.add_argument_group(
        "Actions",
        description="Actions to perform with the Splunk tool. By default, the tool will generate the SPL query, query Splunk, and analyze the response.",
    )
    action_group = actions.add_mutually_exclusive_group()
    action_group.add_argument(
        "-g",
        "--generate",
        dest="generate",
        action="store_true",
        default=False,
        help="Only generate the SPL Query. Expects a question as input.",
    )
    action_group.add_argument(
        "-q",
        "--query",
        dest="query",
        action="store_true",
        default=False,
        help="Only query splunk. Expects a SPL query as input.",
    )
    action_group.add_argument(
        "-a",
        "--analyze",
        dest="analyze",
        action="store_true",
        default=False,
        help="Only analyze the response from Splunk. Expects a question as input and the SQL query results using the --sql-query-results flag.",
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
