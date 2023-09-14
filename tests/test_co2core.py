# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""co2core (core grid, hysteresis, cyclic injection)"""

import os


def test_co2core():
    """See models/co2core.txt"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/models")
    os.system("rm -rf co2core")
    os.system("pyopmnearwell -i co2core.txt -o co2core -p '' ")
    assert os.path.exists("./co2core/output/CO2CORE.UNRST")
    os.system("rm -rf co2core")
    os.chdir(cwd)
