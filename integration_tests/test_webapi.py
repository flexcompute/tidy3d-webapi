import os
import tempfile

import pytest
from requests import HTTPError

from tidy3d_webapi.environment import Env
from tidy3d_webapi.simulation_task import Folder, SimulationTask
from tidy3d_webapi.webapi import (
    delete,
    delete_old,
    download,
    download_json,
    download_log,
    estimate_cost,
    get_info,
    get_run_info,
    get_tasks,
    load,
    load_simulation,
    start,
    upload,
)

Env.dev.active()


def test_upload():
    task = SimulationTask.get("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    sim = task.get_simulation()
    assert upload(sim, "test", "testfolder")


def test_get_info():
    assert get_info("3eb06d16-208b-487b-864b-e9b1d3e010a7")


def test_start():
    task = SimulationTask.get("3eb06d16-208b-487b-864b-e9b1d3e010a7")
    sim = task.get_simulation()
    task = SimulationTask.create(sim, "test task", "test folder1")
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
    task = SimulationTask.create(None, "default", "test delete")
    assert delete(task.task_id)


def test_download_json():
    with tempfile.NamedTemporaryFile(suffix=".json") as hdfile:
        download_json("64a365b2-11e9-4593-a3e0-69361fcc2549", hdfile.name)
        assert os.path.getsize(hdfile.name) > 0


def test_load_simulation():
    with tempfile.NamedTemporaryFile(suffix=".json") as hdfile:
        assert load_simulation("64a365b2-11e9-4593-a3e0-69361fcc2549", hdfile.name)


def test_download_log():
    with tempfile.NamedTemporaryFile(suffix=".log") as hdfile:
        download_log("64a365b2-11e9-4593-a3e0-69361fcc2549", hdfile.name)
        assert os.path.getsize(hdfile.name) > 0


def test_delete_old():
    folder = Folder.create("test delete old")
    SimulationTask.create(None, "test case1", folder.folder_name)
    SimulationTask.create(None, "test case2", folder.folder_name)
    SimulationTask.create(None, "test case3", folder.folder_name)
    SimulationTask.create(None, "test case4", folder.folder_name)
    assert 0 == delete_old(0, folder.folder_name)
    assert 4 == delete_old(-1, folder.folder_name)
    folder.delete()


def test_get_tasks():
    delete_old(-1, "test_get_tasks")
    folder = Folder.create("test_get_tasks")
    task1 = SimulationTask.create(None, "test case1", folder.folder_name)
    task2 = SimulationTask.create(None, "test case2", folder.folder_name)
    task3 = SimulationTask.create(None, "test case3", folder.folder_name)
    task4 = SimulationTask.create(None, "test case4", folder.folder_name)
    assert not get_tasks(0, "old", folder=folder.folder_name)
    tasks = get_tasks(2, "new", folder.folder_name)
    assert tasks[0]["task_id"] == task4.task_id
    task1.delete()
    task2.delete()
    task3.delete()
    task4.delete()
    folder.delete()
