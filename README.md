This is a python package associate with [Tidy3](https://github.com/flexcompute/tidy3d)
for https://tidy3d.simulation.cloud operations.

# Design Philosophy

The design Philosophy of this package is inspired
by [Active Record of Ruby on Rails](https://guides.rubyonrails.org/active_record_basics.html),
here are basic ideas:

* Class methods are used to query and creation.
* Instance methods are used to update and delete.

# Install

```shell
pip install tidy3d-webapi
```

# Setup

The API key can be found in [tidy3d user profile page](https://dev-tidy3d.simulation.cloud/account). There are three
ways to setup the API key:

## command line

Run below command line and flow instructions:

```shell
tidy3d configure
```

## manual setup

```shell
mkdir ~/.tidy3d
echo "SIMCLOUD_APIKEY=tidy3d-25c3ad97-372f-4633-a94f-d4d2be598146" > ~/.tidy3d/config
```

## environment variable

Please notice that the environment variable will override the configuration file.

```shell
export SIMCLOUD_APIKEY="tidy3d-api-key"
```

# API Documentation

## Tidy3d folder

```python
from tidy3d_webapi import Tidy3DFolder

folders = Tidy3dFolder.list()
default_folder = Tidy3dFolder.get("default")
new_folder = Tidy3DFolder.create(name="new_folder")
```

## Tidy3d Task

### Query task

```python
import os
import tempfile
from tidy3d_webapi import Tidy3DFolder, SimulationTask

default_folder = Tidy3dFolder.get("default")
tasks = default_folder.list_tasks()

task = SimulationTask.get("3eb06d16-208b-487b-864b-e9b1d3e010a7")
with tempfile.NamedTemporaryFile() as temp:
    task.get_simulation_json(temp.name)
    assert os.path.exists(temp.name)

sim = task.get_simulation()

```

### Create Task

```python
sim = Simulation.from_file("simulation.json")
task = Tidy3DTask.submit(sim, task_name="test task", folder_name="test folder2")
```

### Task submitting

```python
task = Tidy3DTask.get("3eb06d16-208b-487b-864b-e9b1d3e010a7")
sim = task.get_simulation()
task = Tidy3DTask.submit(sim, "test task", "test folder1")
task.submit(protocol_version="1.6.3")
```

### Remove task

```python
task = Tidy3DTask.get("3eb06d16-208b-487b-864b-e9b1d3e010a7")
task.delete()
```

## Material Fitter

### Private Material Library
```python
from tidy3d_webapi.material_libray import MaterialLibray

libs = MaterialLibray.list()
lib = libs[0]
assert lib.medium
```

### Material fitting and save to library

```python
import time
from tidy3d.plugins import DispersionFitter
from tidy3d_webapi.material_fitter import FitterOptions, MaterialFitterTask

fitter = DispersionFitter.from_file("data/nk_data.csv", skiprows=1, delimiter=",")
task = MaterialFitterTask.submit(fitter, FitterOptions())

retry = 0
max_retry = 12
waiting_sec = 10

while retry < max_retry:
    task.sync_status()  # sync fitter status
    retry += 1
    if task.status == "COMPLETED":
        break
    if task.status != "COMPLETED":
        time.sleep(waiting_sec)

assert task.status == "COMPLETED"
assert task.save_to_library("test_material")  # save to library
```
# Contribution

1. Install poetry
2. Install dependencies: ``poetry install``
3. enable pre-commit hooks for pylint and code reformat ``poetry run autohooks activate --mode poetry``

## check in

1. ``poetry run pytest``
2. ``black .``
3. ``pylint tidy3d_webapi --rcfile .pylintrc``
