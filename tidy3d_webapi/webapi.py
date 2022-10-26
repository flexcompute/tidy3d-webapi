"""Provides lowest level, user-facing interface to server."""

import os

from tidy3d import Simulation, SimulationData
from tidy3d.web.task import TaskId, TaskInfo

from tidy3d_webapi import Tidy3DTask


def upload(  # pylint:disable=too-many-locals,too-many-arguments
    simulation: Simulation, task_name: str, folder_name: str = "default", callback_url: str = None
) -> TaskId:
    """Upload simulation to server, but do not start running :class:`.Simulation`.

    Parameters
    ----------
    simulation : :class:`.Simulation`
        Simulation to upload to server.
    task_name : str
        Name of task.
    folder_name : str
        Name of folder to store task on web UI
    callback_url : str = None
        Http PUT url to receive simulation finish event. The body content is a json file with
        fields ``{'id', 'status', 'name', 'workUnit', 'solverVersion'}``.

    Returns
    -------
    TaskId
        Unique identifier of task on server.

    Note
    ----
    To start the simulation running, must call :meth:`start` after uploaded.
    """
    task = Tidy3DTask.create(simulation, task_name, folder_name, callback_url)
    task.upload_simulation()
    return task.task_id


def get_info(task_id: TaskId) -> TaskInfo:
    """Return information about a task.

    Parameters
    ----------
    task_id : str
        Unique identifier of task on server.  Returned by :meth:`upload`.

    Returns
    -------
    :class:`TaskInfo`
        Object containing information about status, size, credits of task.
    """
    task = Tidy3DTask.get_task(task_id)
    if not task:
        raise ValueError("Task not found.")
    return TaskInfo(**{"taskId": task.task_id, **task.dict()})


def start(task_id: TaskId) -> None:
    """Start running the simulation associated with task.

    Parameters
    ----------

    task_id : str
        Unique identifier of task on server.  Returned by :meth:`upload`.
    solver_version : str
        Supply or override a specific solver version to the task.
    Note
    ----
    To monitor progress, can call :meth:`monitor` after starting simulation.
    """
    task = Tidy3DTask.get_task(task_id)
    if not task:
        raise ValueError("Task not found.")
    task.submit()


def get_run_info(task_id: TaskId):
    """Gets the % done and field_decay for a running task.

    Parameters
    ----------
    task_id : str
        Unique identifier of task on server.  Returned by :meth:`upload`.

    Returns
    -------
    perc_done : float
        Percentage of run done (in terms of max number of time steps).
        Is ``None`` if run info not available.
    field_decay : float
        Average field intensity normlized to max value (1.0).
        Is ``None`` if run info not available.
    """
    task = Tidy3DTask.get_task(task_id)
    if not task:
        raise ValueError("Task not found.")
    return task.get_running_info()


def download(task_id: TaskId, path: str = "simulation_data.hdf5") -> None:
    """Download results of task and log to file.

    Parameters
    ----------
    task_id : str
        Unique identifier of task on server.  Returned by :meth:`upload`.
    path : str = "simulation_data.hdf5"
        Download path to .hdf5 data file (including filename).

    """
    task = Tidy3DTask.get_task(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found.")
    task.get_simulation_hdf5(path)


def load(
    task_id: TaskId,
    path: str = "simulation_data.hdf5",
    replace_existing: bool = True,
) -> SimulationData:
    """Load simulation data from server.

    Parameters
    ----------
    task_id : str
        Unique identifier of task on server.  Returned by :meth:`upload`.
    path : str, optional
        Path to save simulation data to.  Defaults to "simulation_data.hdf5".
    replace_existing : bool, optional
        If True, replace existing file at `path`.  If False, raise an error if
        file already exists.  Defaults to True.

    Returns
    -------
    SimulationData
        Object containing simulation data.
    """
    task = Tidy3DTask.get_task(task_id)
    if not task:
        return None
    if not os.path.exists(path) or replace_existing:
        task.get_simulation_hdf5(path)
    sim_data = SimulationData.from_file(path)
    final_decay_value = sim_data.final_decay_value
    shutoff_value = sim_data.simulation.shutoff
    if (shutoff_value != 0) and (final_decay_value > shutoff_value):
        print(
            f"Simulation final field decay value of {final_decay_value} "
            f"is greater than the simulation shutoff threshold of {shutoff_value}. "
            "Consider simulation again with large run_time duration for more accurate results."
        )

    return sim_data


def delete(task_id: TaskId) -> TaskInfo:
    """Delete server-side data associated with task.

    Parameters
    ----------
    task_id : str
        Unique identifier of task on server.  Returned by :meth:`upload`.

    Returns
    -------
    TaskInfo
        Object containing information about status, size, credits of task.
    """

    task = Tidy3DTask.get_task(task_id)
    task.remove()
    return TaskInfo(**{"taskId": task.task_id, **task.dict()})


def estimate_cost(task_id: str) -> float:
    """
    Estimate cost of a task.
    :param task_id:
    :return:
    """
    task = Tidy3DTask.get_task(task_id)
    if not task:
        raise ValueError("Task not found.")
    resp = task.estimate_cost()
    if not resp:
        raise ValueError("Failed to estimate cost.")
    return resp.get("flex_unit") or 0.0
