# pylint: disable=missing-function-docstring
"""Test the ``pyopmnearwell.utils.runs`` module."""
from __future__ import annotations

import pathlib
from typing import Any

import pytest

from pyopmnearwell.utils.runs import simulations
from pyopmnearwell.utils.writefile import reservoir_files


@pytest.fixture(name="prepare_runfiles")
def fixture_prepare_runfiles(input_dict: dict[str, Any]) -> None:
    reservoir_files(input_dict)


# pylint: disable=unused-argument
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
