# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the plotting script"""

import os
from pyopmnearwell.visualization.plotting import main


def test_plot_all():
    """See visualization/plotting.py"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/models")
    main()
    assert os.path.exists("pressure.csv")
    os.system("rm -rf *.csv *.png")
    os.chdir(cwd)
