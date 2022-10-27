import os
import tempfile

import pytest
from requests import HTTPError

from tidy3d_webapi.environment import Env
from tidy3d_webapi.simulation_task import SimulationTask, Tidy3DFolder

Env.dev.active()


def test_list_tasks():
    resp = Tidy3DFolder.list()
    assert resp is not None
    tasks = resp[0].list_tasks()
    assert tasks is not None


def test_query_task():
    task = SimulationTask.get("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    assert task
    with pytest.raises(HTTPError):
        assert SimulationTask.get("xxx") is None


def test_get_simulation_json():
    task = SimulationTask.get("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    with tempfile.NamedTemporaryFile() as temp:
        task.get_simulation_json(temp.name)
        assert os.path.exists(temp.name)


def test_get_simulation_json():
    task = SimulationTask.get("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    sim = task.get_simulation()
    assert sim


def test_upload():
    task = SimulationTask.get("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    with tempfile.NamedTemporaryFile() as temp:
        task._upload_file(temp.name, "temp.json")


def test_create():
    task = SimulationTask.create(None, "test task", "test folder2")
    assert task.task_id
    task.delete()
    Tidy3DFolder.get("test folder2").delete()


def test_submit():
    task = SimulationTask.get("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    sim = task.get_simulation()
    task = SimulationTask.create(sim, "test task", "test folder1")
    task.submit(protocol_version="1.6.3")


def test_estimate_cost():
    task = SimulationTask.get("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    assert task.estimate_cost()


def test_running_info():
    task = SimulationTask.get("64a365b2-11e9-4593-a3e0-69361fcc2549")
    assert task.get_running_info()


def test_get_log():
    task = SimulationTask.get("64a365b2-11e9-4593-a3e0-69361fcc2549")
    with tempfile.NamedTemporaryFile() as temp:
        task.get_log(temp.name)
        assert os.path.getsize(temp.name) > 0
