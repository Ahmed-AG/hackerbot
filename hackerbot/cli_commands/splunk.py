import click

from hackerbot.tools.splunk import SplunkTool, SplunkToolConfig

@click.command(
    "splunk",
)
@click.argument(
    "input",
    type=str,
    required=True,
)
@click.option(
    "--spl-query-results",
    type=str,
    default="",
    help="SQL query results. Used with the -a/--analyze flag to supply the own SQL query results",
)
@click.option(
    "-g",
    "--generate",
    is_flag=True,
    default=False,
    help="Only generate the SPL Query. Expects a question as input.",
)
@click.option(
    "-q",
    "--query",
    is_flag=True,
    default=False,
    help="Only query splunk. Expects a SPL query as input.",
)
@click.option(
    "-a",
    "--analyze",
    is_flag=True,
    default=False,
    help="Only analyze the response from Splunk. Expects a question as input and the SQL query results using the --sql-query-results flag.",
)
@click.option(
    "-l",
    "--llm",
    type=click.Choice(["llama3", "llama3.1", "llama3.1:70b", "llama3.1:405b"]),
    default="llama3.1",
    help="The Large Language model to use. Default is 'llama3.1'",
)
@click.option(
    '--no-stream',
    is_flag=True,
    help="Disable output streaming. Default Enabled"
)
@click.pass_context
def splunk_command(
    ctx: click.Context,
    input: str,
    spl_query_results: str,
    generate: bool,
    query: bool,
    analyze: bool,
    llm: str,
    no_stream: bool,
):
    """
        Run the Splunk tool
        If no options are provided, the tool will generate the SPL query, query Splunk, and analyze the response.
    """
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    print(f"Running Splunk tool with LLM: {llm} - {no_stream}")

    if generate:
        splunk_generate(
            llm=ctx.obj["llm"],
            input=input,
            no_stream=ctx.obj["no_stream"],
        )
    elif query:
        splunk_query(
            llm=ctx.obj["llm"],
            input=input,
        )
    elif analyze:
        if spl_query_results == "":
            print("SQL query results are required when only performing an analysis using -a/--analyze. Please provide the SQL query results using the --sql-query-results flag. Refer to the help (-h/--help) for more information.")
            exit(1)
        splunk_analyze(
            llm=ctx.obj["llm"],
            input=input,
            spl_query_results=spl_query_results,
            no_stream=ctx.obj["no_stream"],
        )
    else:
        splunk_run(
            llm=ctx.obj["llm"],
            input=input,
            no_stream=ctx.obj["no_stream"],
        )


def splunk_generate(
    llm: str,
    input: str,
    no_stream: bool = False,
) -> str:
    config = SplunkToolConfig(
        llm_model=llm,
    )
    splunk = SplunkTool(
        config=config,
    )

    generated_spl = ""

    if no_stream:
        response = splunk.generate_spl(question=input)
        print(f"\n\nSPL Query: {response}\n\n")
        generated_spl = response
    else:
        response = splunk.stream_generate_spl(question=input)
        print(f"\n\nSPL Query: ", end="", flush=True)
        for chunk in response:
            print(chunk, end="", flush=True)
            generated_spl += chunk
        print("\n\n")
    return generated_spl

def splunk_query(
    llm: str,
    input: str,
) -> list[str]:

    config = SplunkToolConfig(
        llm_model=llm,
    )
    splunk = SplunkTool(
        config=config,
    )

    response = splunk.run_search(spl=input, output_mode='csv')
    table_response = splunk.format_splunk_results_as_table(response, results_mode='csv')
    print(f"\n\nSearch Results:\n\n{table_response}\n\n")

    return response

def splunk_analyze(
    llm: str,
    input: str,
    spl_query_results: str,
    no_stream: bool = False,
) -> str:
    config = SplunkToolConfig(
        llm_model=llm,
    )
    splunk = SplunkTool(
        config=config,
    )

    analysis = ""

    if no_stream:
        response = splunk.analyze_results(question=input, search_results=spl_query_results)
        analysis = response
        print(f"\n\nAnalysis:\n\n{analysis}\n\n")
    else:
        response = splunk.stream_analyze_results(question=input, search_results=spl_query_results)
        print("Analysis:\n\n", end="", flush=True)
        for chunk in response:
            print(chunk, end="", flush=True)
            analysis += chunk
        print("\n\n")

    return analysis

def splunk_run(
    llm: str,
    input: str,
    no_stream: bool = False,
):
    config = SplunkToolConfig(
        llm_model=llm,
    )
    splunk = SplunkTool(
        config=config,
    )


    # if no_stream:
    #     request = SplunkRequest(
    #         question=input,
    #         return_spl=print_spl,
    #     )
    #     response = splunk.run(request)
    #     if print_spl:
    #         print(f"\n\nSPL Query: '{response.spl}'")

    #     print("\n\nAnswer:\n\n")
    #     print(response.answer)
    # else:
    spl = splunk_generate(llm, input, no_stream)
    query_results = splunk_query(llm, spl)
    str_query_results = "".join(query_results)
    analysis = splunk_analyze(llm, input, str_query_results, no_stream)
