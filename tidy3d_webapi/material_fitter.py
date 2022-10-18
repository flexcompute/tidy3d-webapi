"""
Material Fitter API
"""
import os
import tempfile
from enum import Enum
from typing import Optional
from uuid import uuid4

import numpy as np
import requests
from pydantic import BaseModel, Field
from tidy3d.plugins import DispersionFitter

from tidy3d_webapi.http_management import http


class ConstraintEnum(str, Enum):
    """
    Constraint Enum
    """

    HARD = "hard"
    SOFT = "soft"


class FitterOptions(BaseModel):
    """
    Fitter Options
    """

    num_poles: Optional[int] = 1
    num_tries: Optional[int] = 50
    tolerance_rms: Optional[float] = 1e-2
    min_wvl: Optional[float] = None
    max_wvl: Optional[float] = None
    bound_amp: Optional[float] = None
    bound_eps_inf: Optional[float] = 1.0
    bound_f: Optional[float] = None
    constraint: ConstraintEnum = ConstraintEnum.HARD
    nlopt_maxeval: int = 5000


class _FitterRequest(BaseModel):
    fileName: str
    jsonInput: str
    resourcePath: str


class MaterialFitterTask(BaseModel):
    """
    Material Fitter Task
    """

    id: str
    dispersion_fitter: DispersionFitter
    status: str
    file_name: str = Field(..., alias="fileName")
    resource_path: str = Field(..., alias="resourcePath")

    @classmethod
    def create(cls, fitter: DispersionFitter, options: FitterOptions):
        """
        Create a new material fitter task
        :param fitter:
        :param options:
        :return:
        """
        assert fitter
        assert options
        data = np.asarray(list(zip(fitter.wvl_um, fitter.n_data, fitter.k_data)))
        with tempfile.NamedTemporaryFile(suffix=".csv") as temp:
            np.savetxt(temp, data, delimiter=",", header="Wavelength,n,k")
            uid = str(uuid4())
            url = http.get(
                f"tidy3d/fitter/{uid}/signedUrl?filepath={os.path.basename(temp.name)}&method=PUT"
            )
            temp.seek(0)
            resp = requests.put(
                url,
                data=temp.read(),
                headers={"Content-Type": "application/octet-stream"},
                timeout=60,
            )
            if resp.raise_for_status():
                raise resp.raise_for_status()
            fitter_req = _FitterRequest(
                fileName=os.path.basename(temp.name),
                jsonInput=options.json(exclude_none=True),
                resourcePath=uid,
            )
            resp = http.post("tidy3d/fitter/fit", json=fitter_req.dict())
            return cls(dispersion_fitter=fitter, **resp)

    def sync_status(self):
        """
        Sync the status from cloud platform.
        :return:
        """
        resp = http.get(f"tidy3d/fitter/{self.id}")
        self.status = resp["status"]

    def save_to_library(self, name: str) -> bool:
        """
        Save the fitted material to the material library
        :param name:
        :return:
        """

        if self.status != "COMPLETED":
            print("Task is not completed, please use sync_status to get latest status.")
            return False
        resp = http.post("tidy3d/fitter/save", json={"id": self.id, "fitterName": name})
        return resp
