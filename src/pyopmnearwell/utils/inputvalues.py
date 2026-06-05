# SPDX-FileCopyrightText: 2023-2026, NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Utiliy functions to set the requiried input values"""

import sys
import tomllib
import numpy as np


def process_input(dic, in_file):
    """Process the input file"""
    for name in [
        "hysteresis",
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
    dic["zxy"] = "0*x"
    dic["adim"] = 1
    dic["perforations"] = [0, 0, 0]
    dic["ycn"] = [1]
    with open(in_file, "rb") as file:
        dic.update(tomllib.load(file))
    dic["satnum"] = len(dic["rock"]) - dic["perforations"][0]
    dic["fluxnum"] = len(dic["rock"]) > 1
    dic["imbnum"] = 2 if dic["hysteresis"] != 0 else 1
    zdim, znc, dic["homo"], tmp = 0.0, 0, True, dic["rock"][0][3]
    for index, rock in enumerate(dic["rock"]):
        if len(rock) > 3:
            zdim += rock[3]
            znc += rock[4]
            if index > 0 and tmp != rock[3] and dic["homo"]:
                dic["homo"] = False
            tmp = rock[3]
    dic["zcn"] = [znc]
    if dic["grid"] in ["coord2d", "coord3d"]:
        dic["nocells"] = [len(dic["xcn"]) - 1, 1, np.sum(dic["zcn"])]
    else:
        dic["nocells"] = [np.sum(dic["xcn"]), 1, np.sum(dic["zcn"])]
    dic["dims"] = [dic["xdim"], dic["adim"], zdim]
    process_tuning(dic)
    return dic


def process_tuning(dic):
    """Preprocess tuning"""
    dic["tuning"] = any(
        "--enable-tuning" in value and value[16:] in ["true", "True", "1"]
        for value in dic["flow"].split()
    )
    for index, inj in enumerate(dic["inj"]):
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
            dic["inj"][index][-1] = tmp[0].strip()
            if len(tmp) > 1:
                dic["inj"][index].extend(val.strip() for val in tmp[1:])
