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

def version(ctx: click.Context, param: click.Parameter, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    click.echo(f"Running hackerbot v{__version__}")
    ctx.exit()


CONTEXT_SETTINGS = {
    'help_option_names': ['-h', '--help'],
}

@click.group(
    context_settings=CONTEXT_SETTINGS,
    invoke_without_command=True
)
@click.option(
    '-d',
    '--debug',
    is_flag=True,
    is_eager=True,
    callback=set_debug,
    envvar="HACKERBOT_DEBUG",
    help="Enable debug logging. Can also be set with the HACKERBOT_DEBUG environment variable."
)
@click.option(
    '-V',
    '--version',
    is_flag=True,
    is_eager=True,
    callback=version,
    help="Print the version and exit"
)
@click.pass_context
def main(
    ctx: click.Context,
    debug: bool,
    version: bool,
) -> None:
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)

    if ctx.invoked_subcommand is None:
        click.echo("No command provided. Run `hackerbot --help` for more information")

    ctx.obj["debug"] = debug



main.add_command(splunk_command)

