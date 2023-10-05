# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the comparison script"""

import os


def test_plot_comparison():
    """See visualization/plotting.py"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/models")
    os.system("pyopmnearwell -c compare")
    assert os.path.exists("compare/well_pressure.png")
    os.chdir(cwd)
