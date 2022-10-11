"""
tidy3d webapi types
"""
import os.path
import tempfile
from typing import List, Optional

from pydantic import BaseModel, Field, parse_obj_as
from tidy3d import Simulation

from tidy3d_webapi.http_management import http
from tidy3d_webapi.s3utils import download_file, get_s3_sts_token, upload_file

SIMULATION_JSON = "simulation.json"


class Tidy3DFolder(BaseModel):
    """
    Tidy3D Folder
    """

    folder_id: str = Field(..., alias="id")

    @classmethod
    def list(cls, page_number=0, page_size=50) -> []:
        """
        List all folders
        :param page_number:
        :param page_size:
        :return:
        """
        return parse_obj_as(
            List[Tidy3DFolder],
            **http.get("tidy3d/folders", {"page_number": page_number, "page_size": page_size}),
        )

    def list_tasks(self, page_number=0, page_size=50) -> []:
        """
        List all tasks in this folder
        :param page_number:
        :param page_size:
        :return:
        """
        return parse_obj_as(
            List[Tidy3DTask],
            **http.get(
                f"tidy3d/folders/{self.folder_id}/tasks",
                {"page_number": page_number, "page_size": page_size},
            ),
        )


class Tidy3DTask(BaseModel):
    """
    Tidy3D Task
    """

    task_id: Optional[str] = Field(..., alias="id")

    simulation: Optional[Simulation]

    @classmethod
    def get_task(cls, task_id: str):
        """
        Get task by task id
        :param task_id:
        :return:
        """
        return Tidy3DTask(**http.get(f"/tasks/{task_id}"))

    def get_simulation(self) -> Optional[Simulation]:
        """
        Get tidy3d simulation
        :return:
        """
        if self.simulation:
            return self.simulation

        with tempfile.NamedTemporaryFile() as temp:
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
        if self.task_id:
            token = get_s3_sts_token(self.task_id, SIMULATION_JSON)
            client = token.get_client()
            try:
                client.head_object(Bucket=token.get_bucket(), Key=token.get_s3_key())
                download_file(self.task_id, SIMULATION_JSON, to_file=to_file)
            except client.exceptions.ClientError:
                print("Simulation.json not found.")

    def upload_file(self, local_file: str, remote_filename: str):
        """
        Upload file to platform.
        :param local_file:
        :param remote_filename:
        :return:
        """
        if not self.task_id:
            resp = http.post("/tasks", json=self.dict())
            self.task_id = resp.json()["id"]

        upload_file(self.task_id, local_file, remote_filename)

    def submit(self):
        """
        kick off this task.
        :return:
        """
        if self.task_id:
            http.post(f"/tasks/{self.task_id}/submit")
