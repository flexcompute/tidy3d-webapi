"""
Tidy3d webapi types
"""
import os.path
import tempfile
from datetime import datetime
from typing import List, Optional

from pydantic import Extra, Field, parse_obj_as
from tidy3d import Simulation
from tidy3d.version import __version__

from tidy3d_webapi.cache import FOLDER_CACHE
from tidy3d_webapi.http_management import http
from tidy3d_webapi.s3_utils import download_file, upload_file, upload_string
from tidy3d_webapi.tidy3d_types import (
    Queryable,
    ResourceLifecycle,
    Submittable,
    T,
    Tidy3DResource,
)

SIMULATION_JSON = "simulation.json"
SIMULATION_HDF5 = "output/monitor_data.hdf5"
RUNNING_INFO = "output/solver_progress.csv"
LOG_FILE = "output/tidy3d.log"


class Tidy3DFolder(Tidy3DResource, Queryable, extra=Extra.allow):
    """
    Tidy3D Folder
    """

    folder_id: str = Field(..., alias="projectId")
    folder_name: str = Field(..., alias="projectName")

    @classmethod
    def list(cls) -> []:
        """
        List all folders
        :param page_number:
        :param page_size:
        :return:
        """
        resp = http.get("tidy3d/projects")
        return (
            parse_obj_as(
                List[Tidy3DFolder],
                resp,
            )
            if resp
            else None
        )

    @classmethod
    def get(cls, folder_name: str):
        """
        Get folder by name.
        :param folder_name:
        :return:
        """
        resp = http.get(f"tidy3d/project?projectName={folder_name}")
        return Tidy3DFolder(**resp) if resp else None

    @classmethod
    def create(cls, folder_name: str):
        """
        Get folder by name.
        :param folder_name:
        :return:
        """
        folder = Tidy3DFolder.get(folder_name)
        if folder:
            return folder
        resp = http.post("tidy3d/projects", {"projectName": folder_name})
        return Tidy3DFolder(**resp) if resp else None

    def delete(self):
        """
        Remove this folder
        :return:
        """
        http.delete(f"tidy3d/projects/{self.folder_id}")

    def list_tasks(self) -> []:
        """
        List all tasks in this folder
        :return:
        """
        resp = http.get(f"tidy3d/projects/{self.folder_id}/tasks")
        return (
            parse_obj_as(
                List[SimulationTask],
                resp,
            )
            if resp
            else None
        )


class SimulationTask(ResourceLifecycle, Submittable, extra=Extra.allow):
    """Interface for managing the running of a :class:`.Simulation` task on server."""

    task_id: Optional[str] = Field(
        ...,
        title="task_id",
        description="Task ID number, set when the task is uploaded, leave as None.",
        alias="taskId",
    )
    status: Optional[str] = Field(title="status", description="Simulation task status.")
    created_at: Optional[datetime] = Field(title="created_at", alias="createdAt")

    simulation: Optional[Simulation] = Field(
        title="simulation", description="Simulation to run as a 'task'."
    )

    folder: Optional[Tidy3DFolder]

    @classmethod
    def create(
        cls, simulation: Simulation, task_name: str, folder_name="default", call_back_url=None
    ) -> T:
        """
        Create a new task on the server.

        Parameters
        ----------
        path : str = "./simulation_data.hdf5"
            Path to download data as ``.hdf5`` file (including filename).
        :param simulation:
        :param task_name:
        :param folder_name:
        :param call_back_url:

        Returns
        -------
        :class:`TaskInfo`
            :class:`TaskInfo` object containing info about status, size, credits of task and others.
        """
        folder = FOLDER_CACHE.get(folder_name)
        if not folder:
            folder = Tidy3DFolder.get(folder_name)
        if not folder:
            folder = Tidy3DFolder.create(folder_name)
        FOLDER_CACHE[folder_name] = folder

        resp = http.post(
            f"tidy3d/projects/{folder.folder_id}/tasks",
            {"task_name": task_name, "call_back_url": call_back_url},
        )
        return SimulationTask(**resp, simulation=simulation, folder=folder)

    @classmethod
    def get(cls, task_id: str) -> T:
        """
        Get task by task id
        :param task_id:
        :return:
        """
        resp = http.get(f"tidy3d/tasks/{task_id}/detail")
        return SimulationTask(**resp) if resp else None

    def delete(self):
        """
        Remove this task
        :return:
        """
        if not self.task_id:
            raise ValueError("Task id not found.")
        http.delete(f"tidy3d/tasks/{self.task_id}")

    def get_simulation(self) -> Optional[Simulation]:
        """
        Get Tidy3d simulation
        :return:
        """
        if self.simulation:
            return self.simulation

        with tempfile.NamedTemporaryFile(suffix=".json") as temp:
            self.get_simulation_json(temp.name)
            if os.path.exists(temp.name):
                self.simulation = Simulation.from_file(temp.name)
                return self.simulation
        return None

    def get_simulation_json(self, to_file: str):
        """
        Get simulation.json from platform.
        :param to_file:
        :return:
        """
        assert self.task_id
        download_file(self.task_id, SIMULATION_JSON, to_file=to_file)

    def upload_simulation(self):
        """
        Upload simulation object to platform.
        :return:
        """
        assert self.task_id
        assert self.simulation
        upload_string(self.task_id, self.simulation.json(), SIMULATION_JSON)

    def upload_file(self, local_file: str, remote_filename: str):
        """
        Upload file to platform.
        :param local_file:
        :param remote_filename:
        :return:
        """
        assert self.task_id

        upload_file(self.task_id, local_file, remote_filename)

    def submit(self, solver_version=None, worker_group=None, protocol_version=__version__):
        """
        kick off this task.
        :return:
        """
        if self.simulation:
            upload_string(self.task_id, self.simulation.json(), SIMULATION_JSON)
        http.post(
            f"tidy3d/tasks/{self.task_id}/submit",
            {
                "solverVersion": solver_version,
                "workerGroup": worker_group,
                "protocolVersion": protocol_version,
            },
        )

    def estimate_cost(self, solver_version=None, protocol_version=None):
        """
        Estimate cost for this task.
        :return:
        """
        assert self.task_id
        resp = http.post(
            f"tidy3d/tasks/{self.task_id}/metadata",
            {
                "solverVersion": solver_version,
                "protocolVersion": protocol_version,
            },
        )
        return resp

    def get_simulation_hdf5(self, to_file: str):
        """
        Get simulation.json from platform.
        :param to_file:
        :return:
        """
        assert self.task_id
        download_file(self.task_id, SIMULATION_HDF5, to_file=to_file)

    def get_running_info(self):
        """
        Get running info.
        :return:
        """
        assert self.task_id
        with tempfile.NamedTemporaryFile() as temp:
            download_file(self.task_id, RUNNING_INFO, to_file=temp.name, show_progress=False)
            with open(temp.name, "r", encoding="utf-8") as csv:
                progress_string = csv.readlines()
                perc_done, field_decay = progress_string[-1].split(",")
                return float(perc_done), float(field_decay)

    def get_log(self, to_file: str):
        """
        Get log file.
        :return:
        """
        assert self.task_id
        download_file(self.task_id, LOG_FILE, to_file=to_file)
