import tempfile

import pytest
from botocore.exceptions import ClientError

from tidy3d_webapi.environment import Env
from tidy3d_webapi.s3_utils import download_file
from tidy3d_webapi.sts_token import get_s3_sts_token

Env.dev.active()


def test_same_account_and_s3_location():
    # print(get_s3_sts_token("abcde", "simulation.json"))
    with tempfile.NamedTemporaryFile() as temp:
        download_file("3a2585f8-fce9-499b-a1ea-67b2444eaf0d", "simulation.json", temp.name)
        assert temp.name


def test_download_other_account_file():
    with tempfile.NamedTemporaryFile() as temp:
        download_file("abcde", "simulation.json", temp.name, False)
        assert temp.name


def test_sts_token():
    token = get_s3_sts_token("3a2585f8-fce9-499b-a1ea-67b2444eaf0d", "simulation.json")

    client = token.get_client()
    meta_data = client.head_object(Bucket=token.get_bucket(), Key=token.get_s3_key())
    print(meta_data)

    # meta_data = client.head_object(Bucket=token.get_bucket(),
    #                                Key="users/AIDAU77I6BZ25DGMJ633P/3a2585f8-fce9-499b-a1ea-67b2444eaf0d/simulation.json")


def test_sts_cross():
    with pytest.raises(ClientError) as err_info:
        token = get_s3_sts_token
        token = get_s3_sts_token("3a2585f8-fce9-499b-a1ea-67b2444eaf0d", "simulation.json")
        client = token.get_client()
        meta_data = client.head_object(
            Bucket=token.get_bucket(),
            Key="users/AIDAU77I6BZ227VL4JXAN/6054d460-ea30-47f8-96c1-c8baf617668d/cylinder.cgns",
        )
    assert err_info.value.response["Error"] == {"Code": "403", "Message": "Forbidden"}
