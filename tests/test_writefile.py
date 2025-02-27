# pylint: disable=missing-function-docstring
"""Test the ``pyopmnearwell.utils.writefile`` module."""

from __future__ import annotations

import pathlib
from typing import Any

import pytest

from pyopmnearwell.utils.writefile import reservoir_files


@pytest.mark.parametrize("recalc_grid", [True, False])
@pytest.mark.parametrize("recalc_tables", [True, False])
@pytest.mark.parametrize("recalc_sections", [True, False])
def test_reservoir_files(
    input_dict: dict[str, Any],
    recalc_grid: bool,
    recalc_tables: bool,
    recalc_sections: bool,
) -> None:
    reservoir_files(
        input_dict,
        recalc_grid=recalc_grid,
        recalc_tables=recalc_tables,
        recalc_sections=recalc_sections,
    )

    # Check that the expected files were created.
    preprocessing_fol: pathlib.Path = input_dict["fol"] / "preprocessing"
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
