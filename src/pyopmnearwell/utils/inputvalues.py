# SPDX-FileCopyrightText: 2023-2025, NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to set the requiried input values by pynearwell.
"""

import tomllib
import sys
import numpy as np


def process_input(dic, in_file):
    """
    Function to process the input file

    Args:
        dic (dict): Global dictionary with required parameters\n
        in_file (str): Name of the input toml file

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    for name in [
        "hysteresis",
        "zxy",
        "rockcomp",
        "xflow",
        "confact",
        "removecells",
        "econ",
        "xfac",
        "pcfact",
        "salinity",
    ]:
        dic[name] = 0
    dic["adim"] = 1
    dic["perforations"] = [0, 0, 0]
    dic["ycn"] = [1]
    with open(in_file, "rb") as file:
        dic.update(tomllib.load(file))
    dic["satnum"] = len(dic["rock"]) - dic["perforations"][0]
    dic["fluxnum"] = len(dic["rock"]) > 1
    if dic["hysteresis"] != 0:
        dic["imbnum"] = 2
    else:
        dic["imbnum"] = 1
    zdim, znc, dic["homo"], tmp = 0.0, 0, True, dic["rock"][0][3]
    for i, rock in enumerate(dic["rock"]):
        if len(rock) > 3:
            zdim += rock[3]
            znc += rock[4]
            if i > 0:
                if tmp != rock[3] and dic["homo"]:
                    dic["homo"] = False
                tmp = rock[3]
    dic["zcn"] = [znc]
    if dic["grid"] == "coord2d" or dic["grid"] == "coord3d":
        dic["nocells"] = [
            len(dic["xcn"]) - 1,
            1,
            np.sum(dic["zcn"]),
        ]
    else:
        dic["nocells"] = [
            np.sum(dic["xcn"]),
            1,
            np.sum(dic["zcn"]),
        ]
    dic["dims"] = [dic["xdim"], dic["adim"], zdim]
    process_tuning(dic)
    return dic


def process_tuning(dic):
    """
    Preprocess tuning

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["tuning"] = False
    for value in dic["flow"].split():
        if "--enable-tuning" in value:
            if value[16:] in ["true", "True", "1"]:
                dic["tuning"] = True
                break
    for i, inj in enumerate(dic["inj"]):
        size = 6 if dic["model"] == "h2store" and inj[3] < 0 else 5
        if len(inj) == size:
            if not isinstance(inj[-1], str):
                print(
                    "\nAfter the 2025.04 release, column 3 for the maximum solver time "
                    + "step in the injection has been moved to the end of the column, including "
                    + "the items for the TUNING keyword, which gives more control when setting "
                    + "the simulations. Please see the configuration files in the examples and "
                    + "online documentation (Configuration file->Well-related parameters), and "
                    + "update your configuration file accordingly.\n"
                )
                sys.exit()
            tmp = inj[-1].split("/")
            dic["inj"][i][-1] = tmp[0].strip()
            if len(tmp) > 1:
                for val in tmp[1:]:
                    dic["inj"][i].append(val.strip())
