# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the different type of grids"""

import os


def test_geometries():
    """See geometries/"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/geometries")
    conf_fil = sorted([name[:-4] for name in os.listdir(".") if name.endswith(".txt")])
    for file in conf_fil:
        command = f"pyopmnearwell -i {file}.txt -o {file} & wait"
        print(command)
        os.system(command)
        assert os.path.exists(f"./{file}/postprocessing/saturation_2D.png")
        os.system(f"rm -rf {file}")
    os.chdir(cwd)
