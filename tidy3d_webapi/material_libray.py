"""
Material Library API
"""
import json
from typing import List, Optional

from pydantic import Field, parse_obj_as, validator
from tidy3d.components.medium import MediumType

from tidy3d_webapi.http_management import http
from tidy3d_webapi.tidy3d_types import Queryable


class MaterialLibray(Queryable, smart_union=True):
    """
    Material Library
    """

    id: str
    name: str
    medium: Optional[MediumType] = Field(alias="calcResult")
    medium_type: Optional[str] = Field(alias="mediumType")
    json_input: Optional[dict] = Field(alias="jsonInput")

    # pylint: disable=no-self-argument
    @validator("medium", "json_input", pre=True)
    def parse_result(cls, values):
        """
        Convert medium and input from string to object
        """
        return json.loads(values)

    @classmethod
    def list(cls):
        """
        List all material libraries
        :return:
        """
        resp = http.get("tidy3d/libraries")
        return parse_obj_as(List[MaterialLibray], resp) if resp else None
