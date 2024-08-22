import click
import json

from hackerbot.tools.splunk import SplunkToolConfig, SplunkTool
from hackerbot.config import hackerbot_config, DEFAULT_CONFIG_PATH


@click.command(
    "configure",
)
@click.option(      ### Begin: Add the Splunk options
    "--splunk-host",
    type=str,
    help="The Splunk Host",
    default=hackerbot_config.splunk.splunk_host,
    prompt=True,
)
@click.option(
    "--splunk-port",
    type=int,
    help="The Splunk Port",
    default=hackerbot_config.splunk.splunk_port,
    prompt=True,
)
@click.option(
    "--splunk-user",
    type=str,
    help="The Splunk User",
    default=hackerbot_config.splunk.splunk_user,
    prompt=True,
)
@click.option(
    "--splunk-llm-url",
    type=str,
    help="The LLM URL to be used by the Splunk tool",
    default=hackerbot_config.splunk.llm_url,
    prompt=True,
)
@click.option(
    "--splunk-llm-model",
    type=str,
    help="The LLM Model to used by the Splunk tool",
    default=hackerbot_config.splunk.llm_model,
    prompt=True,
)
@click.option(
    "--verify-ssl",
    type=str,
    help="Verify SSL Certificates",
    default=hackerbot_config.splunk.verify_ssl,
    prompt=True,
)                   ### End: Add the Splunk options
def configure_command(
    splunk_llm_url: str,
    splunk_llm_model: str,
    splunk_host: str,
    splunk_port: str | int,
    splunk_user: str,
    verify_ssl: bool,
):
    """Configure hackerbot"""

    hackerbot_config.splunk = configure_splunk_options(
        llm_url=splunk_llm_url,
        llm_model=splunk_llm_model,
        verify_ssl=verify_ssl,
        splunk_host=splunk_host,
        splunk_port=splunk_port,
        splunk_user=splunk_user,
        force_env_map_reload=False,
    )

    click.echo("Finished configuring hackerbot")

    hackerbot_config.save_config_default()
    click.echo(f"Saved configuration to: '{DEFAULT_CONFIG_PATH}'")


def configure_splunk_options(
    llm_url: str,
    llm_model: str,
    verify_ssl: bool,
    splunk_host: str,
    splunk_port: str | int,
    splunk_user: str,
    force_env_map_reload: bool,
) -> SplunkToolConfig:

    splunk_password = click.prompt("Enter the Splunk Password [******]", default=hackerbot_config.splunk.splunk_pass, hide_input=True, type=str, show_default=False)


    supress_warnings = False

    conf = SplunkToolConfig(
        splunk_host=splunk_host,
        splunk_port=splunk_port,
        splunk_user=splunk_user,
        splunk_pass=splunk_password,
        verify_ssl=verify_ssl,
        supress_warnings=True,
        force_env_map_reload=False,
        env_map="not important"
    )

    click.echo("Loading the Splunk Environment Map from the Splunk server. Please wait...\n\n")
    splunk_env_map = SplunkTool(conf)._map_env()
    click.echo("Successfully loaded the Splunk Environment Map from the Splunk server")

    click.echo("Finished configuring Splunk Options")


    return SplunkToolConfig(
        llm_model=llm_model,
        llm_url=llm_url,
        verify_ssl=verify_ssl,
        supress_warnings=supress_warnings,
        splunk_host=splunk_host,
        splunk_port=splunk_port,
        splunk_user=splunk_user,
        splunk_pass=splunk_password,
        env_map=splunk_env_map,
        force_env_map_reload=force_env_map_reload,
    )
