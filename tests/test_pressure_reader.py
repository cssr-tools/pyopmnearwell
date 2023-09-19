# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the script to obtain the pressure at given distance"""

import os
from pyopmnearwell.visualization.getpressure import main


def test_pressure_reader():
    """See visualization/getpressure.py"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/models")
    main()
    os.chdir(cwd)
