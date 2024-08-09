import click
from .version import __version__
from .logging import (
    set_level,
)

from hackerbot.cli_commands import splunk_command

def set_debug(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    print("Setting debug")
    set_level("DEBUG")

@click.group
@click.option(
    "-l",
    "--llm",
    type=click.Choice(["llama3", "llama3.1", "llama3.1:70b", "llama3.1:405b"]),
    default="llama3.1",
    show_default="llama3.1",
    help="The Large Language model to use.",
)
@click.option(
    '--debug',
    is_flag=True,
    is_eager=True,
    callback=set_debug,
    envvar="HACKERBOT_DEBUG",
    help="Enable debug logging"
)
@click.option(
    '--no-stream',
    is_flag=True,
    help="Disable output streaming. Default Enabled"
)
@click.pass_context
def main(
    ctx: click.Context,
    llm: str,
    debug: bool,
    no_stream: bool,
) -> None:
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    ctx.obj["llm"] = llm
    ctx.obj["debug"] = debug
    ctx.obj["no_stream"] = no_stream

@main.command()
def version():
    click.echo(f"Running hackerbot v{__version__}")


main.add_command(splunk_command)

