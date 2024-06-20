# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the plotting script."""

import os
import pathlib

from pyopmnearwell.visualization.plotting import main


def test_plot_all(run_main: pathlib.Path) -> None:
    """See visualization/plotting.py"""
    os.chdir(run_main)
    main()
    assert (run_main / "pressure.csv").exists()
