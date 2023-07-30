# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions for necessary files and variables to run OPM Flow.
"""

import os
import csv
import subprocess
import math as mt
import numpy as np
from mako.template import Template


def reservoir_files(dic):
    """
    Function to write opm-related files by running mako templates

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    mytemplate = Template(
        filename=f"{dic['pat']}/templates/{dic['model']}/saturation_functions.mako"
    )
    var = {"dic": dic}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/jobs/saturation_functions.py",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(f"chmod u+x {dic['exe']}/{dic['fol']}/jobs/saturation_functions.py")
    prosc = subprocess.run(
        ["python", f"{dic['exe']}/{dic['fol']}/jobs/saturation_functions.py"],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")
    # Generation of the x-dir spatial discretization using a telescopic function.
    if dic["x_fac"] != 0:
        dic["xcor"] = np.flip(
            (dic["dims"][0])
            * (np.exp(np.flip(np.linspace(0, dic["x_fac"], dic["noCells"][0] + 1))) - 1)
            / (np.exp(dic["x_fac"]) - 1)
        )
    else:
        dic["xcor"] = np.linspace(0, dic["dims"][0], dic["noCells"][0] + 1)
    dic["xcor"] = dic["xcor"][(dic["diameter"] < dic["xcor"]) | (0 == dic["xcor"])]
    dic["noCells"][0] = len(dic["xcor"]) - 1
    dic = manage_grid(dic)
    dic["zcor"] = np.linspace(0, dic["dims"][2], dic["noCells"][2] + 1)
    dic["x_centers"] = 0.5 * (dic["xcor"][:-1] + dic["xcor"][1:])
    mytemplate = Template(filename=f"{dic['pat']}/templates/{dic['model']}/deck.mako")
    var = {"dic": dic}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{dic['exe']}/{dic['fol']}/preprocessing/RESERVOIR.DATA",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)


def manage_grid(dic):
    """
    Function to handle the grid

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    if dic["grid"] == "cartesian2d":
        dxarray = [
            f'{dic["xcor"][i+1]-dic["xcor"][i]}' for i in range(len(dic["xcor"]) - 1)
        ]
        for _ in range(dic["noCells"][2] - 1):
            dxarray.extend(dxarray[-dic["noCells"][0] :])
        dxarray.insert(0, "DX")
        dxarray.append("/")
        with open(
            f"{dic['exe']}/{dic['fol']}/preprocessing/DX.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("\n".join(dxarray))
    elif dic["grid"] == "radial":
        dxarray = [
            f'{dic["xcor"][i+1]-dic["xcor"][i]}' for i in range(len(dic["xcor"]) - 1)
        ]
        dxarray.insert(0, "DRV")
        dxarray.append("/")
        with open(
            f"{dic['exe']}/{dic['fol']}/preprocessing/DRV.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("\n".join(dxarray))
    elif dic["grid"] == "cake":
        dic["slope"] = mt.tan(0.5 * dic["dims"][1] * mt.pi / 180)
        lol = []
        with open(
            f"{dic['pat']}/templates/common/grid.mako", "r", encoding="utf8"
        ) as file:
            for i, row in enumerate(csv.reader(file, delimiter="#")):
                if i == 3:
                    lol.append(f"    return {dic['z_xy']}")
                elif len(row) == 0:
                    lol.append("")
                else:
                    lol.append(row[0])
        with open(
            f"{dic['exe']}/{dic['fol']}/preprocessing/cpg.mako",
            "w",
            encoding="utf8",
        ) as file:
            file.write("\n".join(lol))
        mytemplate = Template(
            filename=f"{dic['exe']}/{dic['fol']}/preprocessing/cpg.mako"
        )
        var = {"dic": dic}
        filledtemplate = mytemplate.render(**var)
        with open(
            f"{dic['exe']}/{dic['fol']}/preprocessing/CAKE.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write(filledtemplate)
    else:
        if dic["x_fac"] != 0:
            dic["xcorc"] = np.flip(
                (dic["dims"][0])
                * (np.exp(np.flip(np.linspace(0, dic["x_fac"], dic["noCells"][0]))) - 1)
                / (np.exp(dic["x_fac"]) - 1)
            )
        else:
            dic["xcorc"] = np.linspace(0, dic["dims"][0], dic["noCells"][0])
        dic["xcorc"] = dic["xcorc"][
            (dic["diameter"] < dic["xcorc"]) | (0 == dic["xcorc"])
        ]
        dic["xcorc"][0] = 0.25 * dic["xcorc"][1]
        for cord in dic["xcorc"]:
            dic["xcorc"] = np.insert(dic["xcorc"], 0, -cord)
        dxarray = [
            f'{dic["xcorc"][i+1]-dic["xcorc"][i]}' for i in range(len(dic["xcorc"]) - 1)
        ]
        dic["noCells"][0] = 2 * dic["noCells"][0] - 1
        dic["noCells"][1] = dic["noCells"][0]
        dic = d3_grids(dic, dxarray)
    return dic


def d3_grids(dic, dxarray):
    """
    Function to handle the 3d cartesian grid or cave

    Args:
        dic (dict): Global dictionary with required parameters
        dxarray (list): String with the size of the grid cells

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    if dic["grid"] == "cave":
        lol = []
        with open(
            f"{dic['pat']}/templates/common/cave.mako", "r", encoding="utf8"
        ) as file:
            for i, row in enumerate(csv.reader(file, delimiter="#")):
                if i == 3:
                    lol.append(f"    return {dic['z_xy']}")
                elif len(row) == 0:
                    lol.append("")
                else:
                    lol.append(row[0])
        with open(
            f"{dic['exe']}/{dic['fol']}/preprocessing/cpg.mako",
            "w",
            encoding="utf8",
        ) as file:
            file.write("\n".join(lol))
        mytemplate = Template(
            filename=f"{dic['exe']}/{dic['fol']}/preprocessing/cpg.mako"
        )
        var = {"dic": dic}
        filledtemplate = mytemplate.render(**var)
        with open(
            f"{dic['exe']}/{dic['fol']}/preprocessing/CAVE.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write(filledtemplate)
    else:
        dyarray = []
        for i in range(dic["noCells"][1] - 1):
            for _ in range(dic["noCells"][1]):
                dyarray.append(dxarray[i])
            dxarray.extend(dxarray[-dic["noCells"][0] :])
        for _ in range(dic["noCells"][1]):
            dyarray.append(dxarray[dic["noCells"][1] - 1])
        for _ in range(dic["noCells"][2] - 1):
            dxarray.extend(dxarray[-dic["noCells"][0] * dic["noCells"][1] :])
            dyarray.extend(dyarray[-dic["noCells"][0] * dic["noCells"][1] :])
        dxarray.insert(0, "DX")
        dxarray.append("/")
        with open(
            f"{dic['exe']}/{dic['fol']}/preprocessing/DX.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("\n".join(dxarray))
        dyarray.insert(0, "DY")
        dyarray.append("/")
        with open(
            f"{dic['exe']}/{dic['fol']}/preprocessing/DY.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("\n".join(dyarray))
    return dic
