# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the co2eor model"""

import os


def test_co2eor():
    """See models/co2eor.txt"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/models")
    os.system("rm -rf co2eor")
    os.system("pyopmnearwell -i co2eor.txt -o co2eor -p ''")
    assert os.path.exists("./co2eor/output/CO2EOR.UNRST")
    os.system("rm -rf co2eor")
    os.chdir(cwd)
