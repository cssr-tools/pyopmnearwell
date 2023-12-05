# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""salt precipitation"""

import os


def test_saltprec():
    """See models/saltprec.txt"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/models")
    os.system("rm -rf saltprec")
    os.system("pyopmnearwell -i saltprec.txt -o saltprec")
    assert os.path.exists("./saltprec/postprocessing/cumulative_saltprec.png")
    os.chdir(cwd)
