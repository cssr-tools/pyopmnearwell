# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to set the requiried input values by pynearwell.
"""

import tomllib


def process_input(dic, in_file):
    """
    Function to process the input file

    Args:
        dic (dict): Global dictionary with required parameters
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
    if dic["hysteresis"] != 0:
        dic["imbnum"] = 2
    else:
        dic["imbnum"] = 1
    zdim = 0.0
    znc = 0
    for rock in dic["rock"]:
        if len(rock) > 3:
            zdim += rock[3]
            znc += rock[4]
    dic["zcn"] = [znc]
    if dic["grid"] == "coord2d" or dic["grid"] == "coord3d":
        dic["nocells"] = [
            len(dic["xcn"]) - 1,
            1,
            sum(dic["zcn"]),
        ]
    else:
        dic["nocells"] = [
            sum(dic["xcn"]),
            1,
            sum(dic["zcn"]),
        ]
    dic["dims"] = [dic["xdim"], dic["adim"], zdim]
    return dic
