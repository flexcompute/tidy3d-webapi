# Development Setup
0. clone repo
1. Install poetry
2. Install dependencies: ``poetry install``
3. enable pre-commit hooks for pylint and code reformat ``poetry run autohooks activate --mode poetry``


## check in
1. ``poetry run pytest``
2. ``black .``
3. ``pylint tidy3d_webapi --rcfile .pylintrc``

## client config api key

1. ``pip install tidy3d``
2. ``tidy3d configure``
