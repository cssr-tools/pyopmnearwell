# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

# pylint: skip-file
"""Utility functions for necessary files and variables to run OPM Flow."""

from __future__ import annotations

import csv
import math as mt
import os
import pathlib
import subprocess

import numpy as np
from mako.template import Template

from pyopmnearwell.utils.mako import fill_template


def reservoir_files(
    dic,
    **kwargs,
):
    """
    Function to write opm-related files by running mako templates

    Args:
        dic (dict): Global dictionary with required parameters
        **kwargs: Possible kwargs are:
            - recalc_grid (bool): Whether to recalculate the ``GRID.INC``file. Intended
                for ensemble runs, where the saturation functions/geography/etc. do not
                need to be recalculated for each ensemble member. Defaults to True.
            - recalc_tables (bool): Whether to recalculate the ``TABLES.INC``file.
                Defaults to True.
            - recalc_sections (bool): Whether to recalculate the ``GEOLOGY.INC`` and
                ``REGIONS.INC`` files. Defaults to True.
            - inc_folder (pathlib.Path): If any of the mentioned files is not
                recalculated, they are taken from this folder. Defaults to
                ``pathlib.Path("")``.

    Note:
        - All of the ``recalc_*`` options only work for
        ``co2store no_disgas_no_diffusion`` on a ``cake`` grid so far.
        - For other models or grids there will be errors.

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    # Get ``inc_folder`` and ensure it is a ``Path`` objects.
    inc_folder = pathlib.Path(kwargs.get("inc_folder", pathlib.Path("")))

    # default values
    dic.update(
        {
            "multpv_file": "MULTPV.INC",
            "grid_file": "GRID.INC",
            "drv_file": "DRV.INC",
            "dx_file": "DX.INC",
            "dy_file": "DY.INC",
            "tables_file": "TABLES.INC",
            "geology_file": "GEOLOGY.INC",
            "regions_file": "REGIONS.INC",
        }
    )
    if not "fprep" in dic:
        dic["fprep"] = f"{dic['exe']}/{dic['fol']}/preprocessing"
    # Generation of the x-dir spatial discretization using a telescopic function.
    if dic["x_fac"] != 0:
        dic["xcor"] = np.flip(
            (dic["dims"][0])
            * (np.exp(np.flip(np.linspace(0, dic["x_fac"], dic["noCells"][0] + 1))) - 1)
            / (np.exp(dic["x_fac"]) - 1)
        )
    elif dic["grid"] == "tensor2d":
        for i, (name, arr) in enumerate(zip(["xcor"], ["x_n"])):
            dic[f"{name}"] = [0.0]
            for j, num in enumerate(dic[f"{arr}"]):
                for k in range(num):
                    dic[f"{name}"].append(
                        (j + (k + 1.0) / num) * dic["dims"][i] / len(dic[f"{arr}"])
                    )
            dic[f"{name}"] = np.array(dic[f"{name}"])
    elif dic["grid"] == "coord2d":
        dic["xcor"] = dic["x_n"]
    else:
        dic["xcor"] = np.linspace(0, dic["dims"][0], dic["noCells"][0] + 1)
    if dic["removecells"] == 1:
        dic["xcor"] = dic["xcor"][
            (0.5 * dic["diameter"] < dic["xcor"]) | (0 == dic["xcor"])
        ]
    dic["noCells"][0] = len(dic["xcor"]) - 1

    # Either calculate the grid or update the links to all grid files.
    if kwargs.get("recalc_grid", True):
        if dic["grid"] == "core":
            dic = handle_core(dic)
        else:
            dic = manage_grid(dic)
    else:
        dic.update(
            {
                "grid_file": f"'{inc_folder / 'GRID.INC'}'",
                "drv_file": f"'{inc_folder / 'DRV.INC'}'",
                "dx_file": f"'{inc_folder / 'DX.INC'}'",
                "dy_file": f"'{inc_folder / 'DY.INC'}'",
            }
        )

    # If the tables are not recalculated, update the link to the tables file.
    # TODO: Hiding the default value in ``.get`` is dangerous, as this is accessed
    # multiple times. Possibly its better to introduce a local variable or update the
    # dictionary at the start of the funciton.
    if not kwargs.get("recalc_tables", True):
        dic.update({"tables_file": f"'{inc_folder / 'TABLES.INC'}'"})

    # If the sections are not recalculated, update the link to all section files.
    if not kwargs.get("recalc_sections", True):
        dic.update(
            {
                "geology_file": f"'{inc_folder / 'GEOLOGY.INC'}'",
                "regions_file": f"'{inc_folder / 'REGIONS.INC'}'",
                "multpv_file": f"'{inc_folder / 'MULTPV.INC'}'",
            }
        )

    dic["zcor"] = np.linspace(0, dic["dims"][2], dic["noCells"][2] + 1)
    dic["z_centers"] = 0.5 * (dic["zcor"][:-1] + dic["zcor"][1:])
    dic["x_centers"] = 0.5 * (dic["xcor"][:-1] + dic["xcor"][1:])
    dic["layers"] = np.zeros(dic["noCells"][2])
    for i, _ in enumerate(dic["thickness"]):
        dic["layers"] += dic["z_centers"] > sum(dic["thickness"][: i + 1])

    var = {"dic": dic}
    filledtemplate: str = fill_template(
        var,
        filename=os.path.join(
            dic["pat"], "templates", dic["model"], f"{dic['template']}.mako"
        ),
    )
    with open(
        os.path.join(dic["fprep"], f"{dic['runname'].upper()}.DATA"),
        "w",
        encoding="utf-8",
    ) as file:
        file.write(filledtemplate)
    if dic["model"] != "co2eor":
        if kwargs.get("recalc_tables", True):
            manage_tables(dic)
        if kwargs.get("recalc_sections", True):
            manage_sections(dic)


def manage_sections(dic):
    """
    Function to write the include files in the input deck

    Args:
        dic (dict): Global dictionary with required parameters

    """
    sections = ["geology", "regions"]
    if dic["pvMult"] > 0:
        sections.append("multpv")
    if dic["model"] == "saltprec":
        sections.append("permfact")
        if dic["template"] in ["dyncpres", "dyncpresuniform"]:
            sections.append("pcfact")
    for section in sections:
        var = {"dic": dic}
        filledtemplate: str = fill_template(
            var,
            filename=os.path.join(dic["pat"], "templates", "common", f"{section}.mako"),
        )
        with open(
            os.path.join(dic["fprep"], f"{section.upper()}.INC"),
            "w",
            encoding="utf-8",
        ) as file:
            file.write(filledtemplate)


def manage_tables(dic):
    """
    Function to write the saturation function tables

    Args:
        dic (dict): Global dictionary with required parameters

    """
    if dic["model"] in ["co2store", "saltprec"]:
        filename: str = (
            f"{dic['pat']}/templates/common/saturation_functions_format_2.mako"
        )
    else:
        filename = f"{dic['pat']}/templates/common/saturation_functions_format_1.mako"
    var = {"dic": dic}
    filledtemplate: str = fill_template(var, filename=filename)
    with open(
        os.path.join(dic["exe"], dic["fol"], "jobs", "saturation_functions.py"),
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(
        f"chmod u+x {os.path.join(dic['exe'], dic['fol'], 'jobs', 'saturation_functions.py')}"
    )
    prosc = subprocess.run(
        [
            "python",
            os.path.join(dic["exe"], dic["fol"], "jobs", "saturation_functions.py"),
        ],
        check=True,
    )
    if prosc.returncode != 0:
        raise ValueError(f"Invalid result: { prosc.returncode }")


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
            os.path.join(dic["fprep"], "DX.INC"),
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
            os.path.join(dic["fprep"], "DRV.INC"),
            "w",
            encoding="utf8",
        ) as file:
            file.write("\n".join(dxarray))
    elif dic["grid"] == "cake" or dic["grid"] == "tensor2d" or dic["grid"] == "coord2d":
        dic["slope"] = mt.tan(0.5 * dic["dims"][1] * mt.pi / 180)
        lol = []
        with open(
            f"{dic['pat']}/templates/common/grid2d.mako", "r", encoding="utf8"
        ) as file:
            for i, row in enumerate(csv.reader(file, delimiter="#")):
                if i == 3:
                    lol.append(f"    return {dic['z_xy']}")
                elif len(row) == 0:
                    lol.append("")
                else:
                    lol.append(row[0])
        var = {"dic": dic}
        filledtemplate: str = fill_template(var, text="\n".join(lol))
        with open(
            os.path.join(dic["fprep"], "GRID.INC"),
            "w",
            encoding="utf8",
        ) as file:
            file.write(filledtemplate)
    else:
        if dic["grid"] == "coord3d":
            dic["xcorc"] = dic["x_n"]
        else:
            dic = create_3dgrid(dic)
            if dic["model"] != "co2eor":
                for cord in dic["xcorc"]:
                    dic["xcorc"] = np.insert(dic["xcorc"], 0, -cord)
        dxarray = [
            f'{dic["xcorc"][i+1]-dic["xcorc"][i]}' for i in range(len(dic["xcorc"]) - 1)
        ]
        dic["noCells"][0] = len(dic["xcorc"]) - 1
        dic["noCells"][1] = dic["noCells"][0]
        dic = d3_grids(dic, dxarray)
    return dic


def handle_core(dic):
    """
    Function to handle the core geometry

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["coregeometry"] = np.ones(
        dic["noCells"][0] * dic["noCells"][2] * dic["noCells"][2]
    )
    indx = 0
    for k in range(dic["noCells"][2]):
        for j in range(dic["noCells"][2]):
            for i in range(dic["noCells"][0]):
                if (i + 0.5) * dic["dims"][0] / dic["noCells"][0] < dic["dims"][1] or (
                    i + 0.5
                ) * dic["dims"][0] / dic["noCells"][0] > dic["dims"][0] - dic["dims"][
                    1
                ]:
                    if (
                        (k + 0.5) * dic["dims"][2] / dic["noCells"][2]
                        - 0.5 * dic["dims"][2]
                    ) ** 2 + (
                        (j + 0.5) * dic["dims"][2] / dic["noCells"][2]
                        - 0.5 * dic["dims"][2]
                    ) ** 2 > (
                        0.5 * dic["dims"][2] / dic["noCells"][2]
                    ) ** 2:
                        dic["coregeometry"][indx] = 0
                elif (
                    (k + 0.5) * dic["dims"][2] / dic["noCells"][2]
                    - 0.5 * dic["dims"][2]
                ) ** 2 + (
                    (j + 0.5) * dic["dims"][2] / dic["noCells"][2]
                    - 0.5 * dic["dims"][2]
                ) ** 2 > (
                    0.5 * dic["dims"][2]
                ) ** 2:
                    dic["coregeometry"][indx] = 0
                indx += 1
    dic["dims"][1] = dic["dims"][2]
    dic["noCells"][1] = dic["noCells"][2]
    return dic


def d3_grids(dic, dxarray):
    """
    Function to handle the second part of the 3d grids

    Args:
        dic (dict): Global dictionary with required parameters
        dxarray (list): String with the size of the grid cells

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    if dic["grid"] == "cpg3d":
        lol = []
        with open(
            f"{dic['pat']}/templates/common/grid3d.mako", "r", encoding="utf8"
        ) as file:
            for i, row in enumerate(csv.reader(file, delimiter="#")):
                if i == 3:
                    lol.append(f"    return {dic['z_xy']}")
                elif len(row) == 0:
                    lol.append("")
                else:
                    lol.append(row[0])
        var = {"dic": dic}
        filledtemplate: str = fill_template(var, text="\n".join(lol))
        with open(
            f"{dic['fprep']}/GRID.INC",
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
            f"{dic['fprep']}/DX.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("\n".join(dxarray))
        dyarray.insert(0, "DY")
        dyarray.append("/")
        with open(
            f"{dic['fprep']}/DY.INC",
            "w",
            encoding="utf8",
        ) as file:
            file.write("\n".join(dyarray))
    return dic


def create_3dgrid(dic):
    """
    Function to handle the first part of the 3d grids

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    if dic["x_fac"] != 0:
        dic["xcorc"] = np.flip(
            (dic["dims"][0])
            * (np.exp(np.flip(np.linspace(0, dic["x_fac"], dic["noCells"][0] + 1))) - 1)
            / (np.exp(dic["x_fac"]) - 1)
        )
        if dic["removecells"] == 1:
            dic["xcorc"] = dic["xcorc"][
                (dic["diameter"] < dic["xcorc"]) | (0 == dic["xcorc"])
            ]
        dic["xcorc"][0] = 0.25 * dic["xcorc"][1]
    elif dic["grid"] == "tensor3d":
        for i, (name, arr) in enumerate(zip(["xcorc"], ["x_n"])):
            dic[f"{name}"] = [0.0]
            for j, num in enumerate(dic[f"{arr}"]):
                if j == 0:
                    for k in range(num + 1):
                        dic[f"{name}"].append(
                            ((k + 1 + num) / (2 * num + 1))
                            * (2 * dic["dims"][i] / len(2 * dic[f"{arr}"]))
                            - (dic["dims"][i] / len(2 * dic[f"{arr}"]))
                        )
                else:
                    for k in range(num):
                        dic[f"{name}"].append(
                            (j + (k + 1.0) / num) * dic["dims"][i] / len(dic[f"{arr}"])
                        )
            dic[f"{name}"] = np.array(dic[f"{name}"])
        dic["xcorc"] = np.delete(dic["xcorc"], 0)
    else:
        dic["xcorc"] = np.linspace(0, dic["dims"][0], dic["noCells"][0] + 1)
        if dic["removecells"] == 1:
            dic["xcorc"] = dic["xcorc"][
                (dic["diameter"] < dic["xcorc"]) | (0 == dic["xcorc"])
            ]
        if dic["model"] != "co2eor":
            dic["xcorc"][0] = 0.25 * dic["xcorc"][1]
        else:
            map_zcords(dic)
    return dic


def map_zcords(dic):
    """Generate the z array with the grid face locations"""
    dic["zcords"] = [0.0]
    for i in range(dic["satnum"]):
        for _ in range(dic["nz_perlayer"][i]):
            dic["zcords"].append(
                dic["zcords"][-1] + dic["thickness"][i] / dic["nz_perlayer"][i]
            )
