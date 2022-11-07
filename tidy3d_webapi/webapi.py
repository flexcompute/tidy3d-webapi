"""Provides lowest level, user-facing interface to server."""

import os
from datetime import datetime, timedelta
from typing import Dict, List

import pytz
from tidy3d import Simulation, SimulationData
from tidy3d.web.task import TaskId, TaskInfo
from typing_extensions import Literal

from tidy3d_webapi import Folder, SimulationTask


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
    task = SimulationTask.create(simulation, task_name, folder_name, callback_url)
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
    task = SimulationTask.get(task_id)
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
    task = SimulationTask.get(task_id)
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
    task = SimulationTask.get(task_id)
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
    task = SimulationTask.get(task_id)
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
    task = SimulationTask.get(task_id)
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

    task = SimulationTask.get(task_id)
    task.delete()
    return TaskInfo(**{"taskId": task.task_id, **task.dict()})


def estimate_cost(task_id: str) -> float:
    """
    Estimate cost of a task.
    :param task_id:
    :return:
    """
    task = SimulationTask.get(task_id)
    if not task:
        raise ValueError("Task not found.")
    resp = task.estimate_cost()
    if not resp:
        raise ValueError("Failed to estimate cost.")
    return resp.get("flex_unit") or 0.0


def download_json(task_id: TaskId, path: str = "simulation.json") -> None:
    """Download the `.json` file associated with the :class:`.Simulation` of a given task.

    Parameters
    ----------
    task_id : str
        Unique identifier of task on server.  Returned by :meth:`upload`.
    path : str = SIM_FILE_NAME
        Download path to .json file of simulation (including filename).
    """
    task = SimulationTask.get(task_id)
    if not task:
        raise ValueError("Task not found.")
    task.get_simulation_json(path)


def load_simulation(task_id: TaskId, path: str = "simulation.json") -> Simulation:
    """Download the `.json` file of a task and load the associated :class:`.Simulation`.

    Parameters
    ----------
    task_id : str
        Unique identifier of task on server.  Returned by :meth:`upload`.
    path : str = SIM_FILE_NAME
        Download path to .json file of simulation (including filename).

    Returns
    -------
    :class:`.Simulation`
        Simulation loaded from downloaded json file.
    """
    download_json(task_id, path)
    return Simulation.from_file(path)


def download_log(task_id: TaskId, path: str = "tidy3d.log") -> None:
    """Download the tidy3d log file associated with a task.

    Parameters
    ----------
    task_id : str
        Unique identifier of task on server.  Returned by :meth:`upload`.
    path : str = "tidy3d.log"
        Download path to log file (including filename).

    Note
    ----
    To load downloaded results into data, call :meth:`load` with option `replace_existing=False`.
    """
    task = SimulationTask.get(task_id)
    if not task:
        raise ValueError("Task not found.")
    task.get_log(path)


def delete_old(
    days_old: int = 100,
    folder: str = "default",
) -> int:
    """Delete all tasks older than a given amount of days.

    Parameters
    ----------
    folder : str
        Only allowed to delete in one folder at a time.
    days_old : int = 100
        Minimum number of days since the task creation.

    Returns
    -------
    int
        Total number of tasks deleted.
    """
    folder = Folder.get(folder)
    if not folder:
        return 0
    tasks = folder.list_tasks()
    if not tasks:
        return 0
    tasks = list(
        filter(lambda t: t.created_at < datetime.now(pytz.utc) - timedelta(days=days_old), tasks)
    )
    for task in tasks:
        task.delete()
    return len(tasks)


def get_tasks(
    num_tasks: int = None, order: Literal["new", "old"] = "new", folder: str = "default"
) -> List[Dict]:
    """Get a list with the metadata of the last ``num_tasks`` tasks.

    Parameters
    ----------
    num_tasks : int = None
        The number of tasks to return, or, if ``None``, return all.
    order : Literal["new", "old"] = "new"
        Return the tasks in order of newest-first or oldest-first.
    folder: str = "default"
        Folder from which to get the tasks.
    """
    folder = Folder.get(folder)
    tasks = folder.list_tasks()
    if order == "new":
        tasks = sorted(tasks, key=lambda t: t.created_at, reverse=True)
    elif order == "old":
        tasks = sorted(tasks, key=lambda t: t.created_at)
    if num_tasks is not None:
        tasks = tasks[:num_tasks]
    return [task.dict() for task in tasks]
