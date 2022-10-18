from tidy3d_webapi.environment import Env
from tidy3d_webapi.s3_utils import upload_file
from tidy3d_webapi.sts_token import STSTokenType, get_s3_sts_token

Env.dev.active()


def test_get_s3_sts_token():
    upload_file(
        "5f7b3b5b5c5c5c5c5c5c5c5c", "data/nk_data.csv", "nk_data.csv", STSTokenType.FITTER_RESOURCE
    )
