# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the script to obtain the pressure at given distance"""

import os
import pathlib

from pyopmnearwell.visualization.getpressure import main

dirname: pathlib.Path = pathlib.Path(__file__).parent


def test_pressure_reader():
    """See visualization/getpressure.py"""
    os.chdir(dirname / "models")
    main()
