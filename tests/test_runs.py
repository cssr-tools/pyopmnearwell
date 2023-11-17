# pylint: skip-file
from __future__ import annotations

import pathlib
from typing import Any

import pytest

from pyopmnearwell.utils.inputvalues import process_input
from pyopmnearwell.utils.runs import simulations
from pyopmnearwell.utils.writefile import reservoir_files

dirname: pathlib.Path = pathlib.Path(__file__).parent


@pytest.fixture
def input_dict(tmp_path: pathlib.Path) -> dict[str, Any]:
    """Manually do what ``pyopmnearwell.py`` does."""
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


@pytest.fixture
def prepare_runfiles(input_dict: dict[str, Any]) -> None:
    reservoir_files(input_dict)


def test_simulations(input_dict: dict[str, Any], prepare_runfiles: None):
    simulations(input_dict)

    # Check that the expected files were created.
    output_fol: pathlib.Path = input_dict["exe"] / input_dict["fol"] / "output"
    assert (output_fol / "TEST_RUN.EGRID").exists()
    assert (output_fol / "xspace.npy").exists()
    assert (output_fol / "zspace.npy").exists()
    assert (output_fol / "ny.npy").exists()
    assert (output_fol / "schedule.npy").exists()
    assert (output_fol / "radius.npy").exists()
    assert (output_fol / "angle.npy").exists()
    assert (output_fol / "position.npy").exists()
