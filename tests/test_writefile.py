# pylint: skip-file
from __future__ import annotations

import pathlib
from typing import Any

import pytest

from pyopmnearwell.utils.inputvalues import process_input
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


@pytest.mark.parametrize("recalc_grid", [True, False])
@pytest.mark.parametrize("recalc_tables", [True, False])
@pytest.mark.parametrize("recalc_sections", [True, False])
def test_reservoir_files(
    input_dict: dict[str, Any],
    recalc_grid: bool,
    recalc_tables: bool,
    recalc_sections: bool,
) -> None:
    reservoir_files(input_dict, recalc_grid, recalc_tables, recalc_sections)

    # Check that the expected files were created.
    preprocessing_fol: pathlib.Path = (
        input_dict["exe"] / input_dict["fol"] / "preprocessing"
    )
    assert (preprocessing_fol / "TEST_RUN.DATA").exists()
    if recalc_grid:
        assert (preprocessing_fol / "GRID.INC").exists()
    else:
        assert not (preprocessing_fol / "GRID.INC").exists()
    if recalc_tables:
        assert (preprocessing_fol / "TABLES.INC").exists()
    else:
        assert not (preprocessing_fol / "TABLES.INC").exists()
    if recalc_sections:
        assert (preprocessing_fol / "GEOLOGY.INC").exists()
        assert (preprocessing_fol / "REGIONS.INC").exists()
        assert (preprocessing_fol / "MULTPV.INC").exists()
    else:
        assert not (preprocessing_fol / "GEOLOGY.INC").exists()
        assert not (preprocessing_fol / "REGIONS.INC").exists()
        assert not (preprocessing_fol / "MULTPV.INC").exists()
