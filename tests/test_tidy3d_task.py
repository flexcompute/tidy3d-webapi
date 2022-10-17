import os
import tempfile

import pytest
from requests import HTTPError

from tidy3d_webapi import __version__
from tidy3d_webapi.environment import Env
from tidy3d_webapi.types import Tidy3DFolder, Tidy3DTask

Env.dev.active()


def test_version():
    assert __version__ == "0.1.0"


def test_list_tasks():
    resp = Tidy3DFolder.list()
    assert resp is not None
    tasks = resp[0].list_tasks()
    assert tasks is not None


def test_query_task():
    task = Tidy3DTask.get_task("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    assert task
    with pytest.raises(HTTPError):
        assert Tidy3DTask.get_task("xxx") is None


def test_get_simulation_json():
    task = Tidy3DTask.get_task("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    with tempfile.NamedTemporaryFile() as temp:
        task.get_simulation_json(temp.name)
        assert os.path.exists(temp.name)


def test_get_simulation_json():
    task = Tidy3DTask.get_task("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    sim = task.get_simulation()
    assert sim


def test_upload():
    task = Tidy3DTask.get_task("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    with tempfile.NamedTemporaryFile() as temp:
        task._upload_file(temp.name, "temp.json")


def test_create():
    task = Tidy3DTask.create(None, "test task", "test folder2")
    assert task.task_id
    task.remove()
    Tidy3DFolder.get("test folder2").remove()


def test_submit():
    task = Tidy3DTask.get_task("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    sim = task.get_simulation()
    task = Tidy3DTask.create(sim, "test task", "test folder1")
    task.submit(protocol_version="1.6.3")
