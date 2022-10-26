import os
import tempfile

import pytest
from requests import HTTPError

from tidy3d_webapi.environment import Env
from tidy3d_webapi.types import Tidy3DFolder, Tidy3DTask
from tidy3d_webapi.webapi import (
    delete,
    download,
    estimate_cost,
    get_info,
    get_run_info,
    load,
    start,
    upload,
)

Env.dev.active()


def test_upload():
    task = Tidy3DTask.get_task("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    sim = task.get_simulation()
    assert upload(sim, "test", "testfolder")


def test_get_info():
    assert get_info("3eb06d16-208b-487b-864b-e9b1d3e010a7")


def test_start():
    task = Tidy3DTask.get_task("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    sim = task.get_simulation()
    task = Tidy3DTask.create(sim, "test task", "test folder1")
    task.upload_simulation()
    start(task.task_id)


def test_run_info():
    assert get_run_info("64a365b2-11e9-4593-a3e0-69361fcc2549") == (100.0, 2.5583e-05)


def test_download_hdf5():
    with tempfile.NamedTemporaryFile(suffix=".hdf5") as hdfile:
        download("64a365b2-11e9-4593-a3e0-69361fcc2549", hdfile.name)
        assert os.path.getsize(hdfile.name) > 0


def test_load():
    with tempfile.NamedTemporaryFile(suffix=".hdf5") as hdfile:
        assert load("64a365b2-11e9-4593-a3e0-69361fcc2549", hdfile.name)


def test_estimate_cost():
    assert estimate_cost("3eb06d16-208b-487b-864b-e9b1d3e010a7") == 0.1


def test_delete():
    task = Tidy3DTask.create(None, "default", "test delete")
    assert delete(task.task_id)
