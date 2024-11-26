# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the comparison script."""

import os
import pathlib


def test_plot_comparison(run_all_models: pathlib.Path) -> None:
    """See visualization/plotting.py"""
    os.chdir(run_all_models)
    os.system("pyopmnearwell -c compare -p opm")
    assert (run_all_models / "compare" / "well_pressure.png").exists()
