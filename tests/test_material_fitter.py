import time

from tidy3d.plugins import DispersionFitter

from tidy3d_webapi.environment import Env
from tidy3d_webapi.material_fitter import FitterOptions, MaterialFitterTask

Env.dev.active()


def test_material_fitter():
    fitter = DispersionFitter.from_file("data/nk_data.csv", skiprows=1, delimiter=",")
    task = MaterialFitterTask.submit(fitter, FitterOptions())

    retry = 0
    max_retry = 12
    waiting_sec = 10

    while retry < max_retry:
        task.sync_status()
        retry += 1
        if task.status == "COMPLETED":
            break
        if task.status != "COMPLETED":
            time.sleep(waiting_sec)

    assert task.status == "COMPLETED"
    assert task.save_to_library("test_material")
