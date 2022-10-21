from os.path import expanduser

import toml
from click.testing import CliRunner

from tidy3d_webapi.cli import tidy3d_cli

home = expanduser("~")


def test_configure():
    runner = CliRunner()
    runner.invoke(tidy3d_cli, ["configure"], input="apikey")
    result = runner.invoke(tidy3d_cli, ["configure"], input="apikey")
    assert result.exit_code == 0
    assert result.output == "API Key[apikey]: apikey\ndone.\n"
    with open(f"{home}/.tidy3d/config", "r") as f:
        config = toml.loads(f.read())
        assert config.get("apikey", "") == "apikey"
