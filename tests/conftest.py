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
    for name in ["preprocessing", "output", "postprocessing"]:
        (tmp_path / "output" / name).mkdir(parents=True, exist_ok=True)
    # Read input deck.
    base_dict: dict[str, Any] = {
        "pat": dirname / ".." / "src" / "pyopmnearwell",
        "fol": tmp_path / "output",
        "runname": "test_run",
        "model": "co2store",
        "plot": "ecl",
    }
    return process_input(base_dict, dirname / "models" / "co2store.toml")


@pytest.fixture(scope="session", name="run_path")
def fixture_create_path(tmp_path_factory: Any) -> pathlib.Path:
    """Create a temporary path for the run.

    This fixture is used by ``test_runs.py``.

    """
    return tmp_path_factory.mktemp("run")


@pytest.fixture(scope="session", name="run_main")
def fixture_run_main(tmp_path_factory) -> pathlib.Path:
    """Run pyopmnearwell on the ``tests/models/input.toml`` deck.

    Note: In comparison to the ``fixture_run_model`` fixture, the ``main`` function of
        pyopmnearwell is called directly.

    This fixture is used by ``test_main.py``.

    """
    shared_dir: pathlib.Path = tmp_path_factory.mktemp("shared")
    shutil.copy((dirname / "models" / "input").with_suffix(".toml"), shared_dir)
    os.chdir(shared_dir)
    main()
    return shared_dir


@pytest.fixture(scope="session", name="run_model")
def fixture_run_model(request, tmp_path_factory) -> tuple[str, pathlib.Path]:
    """Run pyopmnearwell on the requested deck in ``tests/models``.

    Note: In comparison to the ``fixture_run_main`` fixture, pyopmnearwell is invoked
        via the command line.

    This fixture is used by ``test_models.py``.

    """
    shared_dir: pathlib.Path = tmp_path_factory.mktemp("shared")
    model: str = request.param

    shutil.copy((dirname / "models" / model).with_suffix(".toml"), shared_dir)
    os.chdir(shared_dir)
    os.system(f"pyopmnearwell -i {model}.toml -o {model}")
    return model, shared_dir


@pytest.fixture(scope="session", name="run_all_models")
def fixture_run_all_models(tmp_path_factory) -> pathlib.Path:
    """Run pyopmnearwell on selected decks in ``tests/models``.

    This fixture is used by ``test_plot_comparison.py``.

    """
    # This is a bit hacky, as all models are run twice, once when ``fixture_run_model``
    # is called by ``test_models`` and once here. However, I didn't find any other easy
    # way to ensure that multiple model files are available in the temporary dir s.t.
    # ``pyopmnearwell -c compare`` can be called.
    shared_dir: pathlib.Path = tmp_path_factory.mktemp("shared")
    models: list[str] = ["co2store", "h2store", "saltprec"]
    for model in models:
        shutil.copy((dirname / "models" / model).with_suffix(".toml"), shared_dir)
        os.chdir(shared_dir)
        os.system(f"pyopmnearwell -i {model}.toml -o {model}")
    return shared_dir
