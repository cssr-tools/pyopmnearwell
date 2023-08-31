# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the h2store model with the 3d cartesian grid"""

import os


def test_h2store():
    """See models/h2store.txt"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/models")
    os.system("rm -rf h2store")
    os.system("pyopmnearwell -i h2store.txt -o h2store")
    assert os.path.exists("./h2store/postprocessing/pressure_2D.png")
    os.chdir(cwd)
