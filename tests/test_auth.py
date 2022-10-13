import os
from os.path import expanduser

import pytest
import requests
from click.testing import CliRunner

from tidy3d_webapi.http_management import api_key, api_key_auth


def test_apikey_auth():
    r = requests.Request()

    if os.path.exists(f"{expanduser('~')}/.tidy3d/config"):
        os.remove(f"{expanduser('~')}/.tidy3d/config")
    with pytest.raises(
        ValueError,
        match="API key not found, please set it by commandline or environment, eg: tidy3d configure or export SIMCLOUD_APIKEY=xxx",
    ):
        api_key_auth(r)

    runner = CliRunner()
    from tidy3d_webapi.cli import tidy3d_cli

    runner.invoke(tidy3d_cli, ["configure"], input="apikey")
    r = requests.Request()
    api_key_auth(r)
    assert r.headers["simcloud-api-key"] == "apikey"

    os.environ["SIMCLOUD_APIKEY"] = "apikey1"
    assert api_key() == "apikey1"
