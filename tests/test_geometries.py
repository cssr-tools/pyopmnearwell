# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the different type of grids"""

import os
import math as mt


def test_geometries():
    """See geometries/"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/geometries")
    npr = 5
    conf_fil = sorted([name[:-4] for name in os.listdir(".") if name.endswith(".txt")])
    nsimulations = len(conf_fil)
    for i in range(mt.floor(nsimulations / npr)):
        command = ""
        for j in range(npr):
            command += (
                f"pyopmnearwell -i {conf_fil[npr*i+j]}.txt -o {conf_fil[npr*i+j]} & "
            )
        command += "wait"
        os.system(command)
    finished = npr * mt.floor(nsimulations / npr)
    remaining = nsimulations - finished
    command = ""
    for i in range(remaining):
        command += (
            f"pyopmnearwell -i {conf_fil[finished+i]}.txt -o {conf_fil[finished+i]} & "
        )
    command += "wait"
    os.system(command)
    for i in range(nsimulations):
        assert os.path.exists(f"./{conf_fil[i]}/postprocessing/saturation_2D.png")
        os.system(f"rm -rf {conf_fil[i]}")
    os.chdir(cwd)
