"""Provide fixtures that are used in multiple test modules."""

import os
import pathlib
import shutil
from typing import Any

import pytest

from pyopmnearwell.core.pyopmnearwell import main
from pyopmnearwell.utils.inputvalues import process_input

dirname: pathlib.Path = pathlib.Path(__file__).parent


@pytest.fixture(name="input_dict")
def fixture_input_dict(tmp_path: pathlib.Path) -> dict[str, Any]:
    """Manually do what ``pyopmnearwell.py`` does.

    This fixture is used by ``test_runs.py`` and ``test_writefile.py``.

    """
    # Create run folders.
    for name in ["preprocessing", "jobs", "output", "postprocessing"]:
        (tmp_path / "output" / name).mkdir(parents=True, exist_ok=True)
    # Read input deck.
    base_dict: dict[str, Any] = {
        "pat": dirname / ".." / "src" / "pyopmnearwell",
        "exe": tmp_path,
        "fol": "output",
        "runname": "test_run",
        "model": "co2store",
        "plot": "ecl",
    }
    return process_input(base_dict, dirname / "models" / "co2store.txt")


@pytest.fixture(scope="session", name="run_path")
def fixture_create_path(tmp_path_factory: Any) -> pathlib.Path:
    """Create a temporary path for the run.

    This fixture is used by ``test_runs.py``.

    """
    return tmp_path_factory.mktemp("run")


@pytest.fixture(scope="session", name="run_main")
def fixture_run_main(tmp_path_factory) -> pathlib.Path:
    """Run pyopmnearwell on the requested deck in ``tests/models``.

    Note: For the ``input`` deck, the ``main`` function is called directly, while for
    all other models pyopmnearwell is invoked via the command line.

    This fixture is used by ``test_main.py``.

    """
    shared_dir: pathlib.Path = tmp_path_factory.mktemp("shared")
    shutil.copy((dirname / "models" / "input").with_suffix(".txt"), shared_dir)
    os.chdir(shared_dir)
    main()
    return shared_dir


@pytest.fixture(scope="session", name="run_models")
def fixture_run_models(request, tmp_path_factory) -> tuple[str, pathlib.Path]:
    """Run pyopmnearwell on the requested deck in ``tests/models``.

    Note: For the ``input`` deck, the ``main`` function is called directly, while for
    all other models pyopmnearwell is invoked via the command line.

    This fixture is used by ``test_models.py``.

    """
    shared_dir: pathlib.Path = tmp_path_factory.mktemp("shared")
    model: str = request.param

    shutil.copy((dirname / "models" / model).with_suffix(".txt"), shared_dir)
    os.chdir(shared_dir)
    os.system(f"pyopmnearwell -i {model}.txt -o {model}")
    return model, shared_dir
