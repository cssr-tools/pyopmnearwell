# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the script to obtain the pressure at given distance"""

import os
import pathlib

from pyopmnearwell.visualization.getpressure import main


def test_pressure_reader(run_main: pathlib.Path) -> None:
    """See visualization/getpressure.py"""
    os.chdir(run_main)
    main()
