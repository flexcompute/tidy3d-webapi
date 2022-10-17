"""
STS token management
"""
import urllib
from datetime import datetime

import boto3
from pydantic import BaseModel, Field

from tidy3d_webapi.cache import S3_STS_TOKENS
from tidy3d_webapi.environment import Env
from tidy3d_webapi.http_management import http


class _UserCredential(BaseModel):
    access_key_id: str = Field(alias="accessKeyId")
    expiration: datetime
    secret_access_key: str = Field(alias="secretAccessKey")
    session_token: str = Field(alias="sessionToken")


class _S3STSToken(BaseModel):
    cloud_path: str = Field(alias="cloudpath")
    user_credential: _UserCredential = Field(alias="userCredentials")

    def get_bucket(self) -> str:
        """
        @return: bucket name
        """
        url = urllib.parse.urlparse(self.cloud_path)
        return url.netloc

    def get_s3_key(self) -> str:
        """@return: s3 key"""
        url = urllib.parse.urlparse(self.cloud_path)
        return url.path[1:]

    def get_client(self) -> boto3.client:
        """
        @return: boto3 client

        """
        return boto3.client(
            "s3",
            region_name=Env.current.aws_region,
            aws_access_key_id=self.user_credential.access_key_id,
            aws_secret_access_key=self.user_credential.secret_access_key,
            aws_session_token=self.user_credential.session_token,
        )

    def is_expired(self) -> bool:
        """
        @return: True if token is expired
        @return:
        """
        return (
            self.user_credential.expiration
            - datetime.now(tz=self.user_credential.expiration.tzinfo)
        ).total_seconds() < 300


def get_s3_sts_token(resource_id: str, file_name: str) -> _S3STSToken:
    """
    get s3 sts token for the given resource id and file name
    @param resource_id: the resource id, e.g. task id"
    @param file_name: the remote file name on S3
    @return: _S3STSToken
    """
    cache_key = f"{resource_id}:{file_name}"
    if cache_key not in S3_STS_TOKENS or S3_STS_TOKENS[cache_key].is_expired():
        method = f"tidy3d/tasks/{resource_id}/file?filename={file_name}"
        resp = http.get(method)
        token = _S3STSToken.parse_obj(resp)
        S3_STS_TOKENS[cache_key] = token
    return S3_STS_TOKENS[cache_key]
