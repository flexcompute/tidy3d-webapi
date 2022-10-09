"""
Commandline interface for tidy3d.
"""
import os.path
from os.path import expanduser

import click
import toml

home = expanduser("~")
if os.path.exists(f"{home}/.tidy3d/config"):
    with open(f"{home}/.tidy3d/config", "r", encoding="utf-8") as f:
        content = f.read()
        config = toml.loads(content)
        config_description = f"API Key[{config.get('apikey', '')}]"


@click.group()
def tidy3d_cli():
    """
    Tidy3d command line tool.
    """


@click.command()
@click.option(
    "--apikey", prompt=config_description if "config_description" in globals() else "API Key"
)
def configure(apikey):
    """
    Configure Tidy3d credentials,eg: tidy3d configure

    :param apikey:
    :return:
    """

    with open(f"{home}/.tidy3d/config", "w+", encoding="utf-8") as config_file:
        toml_config = toml.loads(config_file.read())
        toml_config.update({"apikey": apikey})
        config_file.write(toml.dumps(toml_config))
        click.echo("done.")


tidy3d_cli.add_command(configure)
