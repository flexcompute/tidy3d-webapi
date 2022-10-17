"""
tidy3d webapi types
"""
import os.path
import tempfile
from typing import List, Optional

from pydantic import BaseModel, Extra, Field, parse_obj_as
from tidy3d import Simulation
from tidy3d.version import __version__

from tidy3d_webapi.cache import FOLDER_CACHE
from tidy3d_webapi.http_management import http
from tidy3d_webapi.s3_utils import download_file, upload_file, upload_string

SIMULATION_JSON = "simulation.json"


class Tidy3DFolder(BaseModel, extra=Extra.allow):
    """
    Tidy3D Folder
    """

    folder_id: str = Field(..., alias="projectId")
    project_name: str = Field(..., alias="projectName")

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
    def get(cls, project_name: str):
        """
        Get folder by name.
        :param project_name:
        :return:
        """
        resp = http.get(f"tidy3d/project?projectName={project_name}")
        return Tidy3DFolder(**resp) if resp else None

    @classmethod
    def create(cls, project_name: str):
        """
        Get folder by name.
        :param project_name:
        :return:
        """
        resp = http.post("tidy3d/projects", {"projectName": project_name})
        return Tidy3DFolder(**resp) if resp else None

    def remove(self):
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
                List[Tidy3DTask],
                resp,
            )
            if resp
            else None
        )


class Tidy3DTask(BaseModel, extra=Extra.allow):
    """
    Tidy3D Task
    """

    task_id: Optional[str] = Field(..., alias="taskId")
    status: Optional[str]

    simulation: Optional[Simulation]

    folder: Optional[Tidy3DFolder]

    @classmethod
    def create(
        cls, simulation: Simulation, task_name: str, folder_name="default", call_back_url=None
    ):
        """
        Create a new task.
        :param simulation:
        :param task_name:
        :param folder_name:
        :param call_back_url:
        :return:
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
        return Tidy3DTask(**resp, simulation=simulation, folder=folder)

    @classmethod
    def get_task(cls, task_id: str):
        """
        Get task by task id
        :param task_id:
        :return:
        """
        resp = http.get(f"tidy3d/tasks/{task_id}/detail")
        return Tidy3DTask(**resp) if resp else None

    def remove(self):
        """
        Remove this task
        :return:
        """
        if not self.task_id:
            raise ValueError("Task id not found.")
        http.delete(f"tidy3d/tasks/{self.task_id}")

    def get_simulation(self) -> Optional[Simulation]:
        """
        Get tidy3d simulation
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
        download_file(self.task_id, SIMULATION_JSON, to_file=to_file)

    def _upload_file(self, local_file: str, remote_filename: str):
        """
        Upload file to platform.
        :param local_file:
        :param remote_filename:
        :return:
        """
        if not self.task_id:
            raise ValueError("Task id not found.")

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
