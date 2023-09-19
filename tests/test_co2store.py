# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""co2store (cake grid, hysteresis, cyclic injection, perforations)"""

import os


def test_co2store():
    """See models/co2store.txt"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/models")
    os.system("rm -rf co2store")
    os.system("pyopmnearwell -i co2store.txt -o co2store")
    assert os.path.exists("./co2store/postprocessing/concentration_2D.png")
    os.chdir(cwd)
