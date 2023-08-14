# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utiliy functions to set the requiried input values by pynearwell.
"""

import csv
from io import StringIO
import numpy as np


def process_input(dic, in_file):
    """
    Function to process the input file

    Args:
        dic (dict): Global dictionary with required parameters
        in_file (str): Name of the input text file

    Returns:
        dic (dict): Global dictionary with new added parameters
    """
    lol = []
    with open(in_file, "r", encoding="utf8") as file:
        for row in csv.reader(file, delimiter="#"):
            lol.append(row)
    dic, index = readthefirstpart(lol, dic)
    dic = readthesecondpart(lol, dic, index)
    return dic


def readthefirstpart(lol, dic):
    """
    Function to process the first lines from the configuration file

    Args:
        lol (list): List of lines read from the input file
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters
        inc (int): Number of line in the input file
    """
    dic["flow"] = str(lol[1])[2:-2]  # Path to the flow executable
    dic["model"] = (
        str(lol[4][0]).strip().split()[0]
    )  # Physical model (co2store/h2store)
    dic["grid"] = (
        lol[5][0].strip().split()[0]
    )  # Grid type (radial/cake/cartesian2d/cartesian)
    dic["dims"] = [float((lol[6][0].strip()).split()[j]) for j in range(2)]
    dic["dims"].insert(1, float(lol[5][0].strip().split()[1]))
    if dic["grid"] == "tensor2d" or dic["grid"] == "tensor3d":
        dic["x_n"] = np.genfromtxt(
            StringIO((lol[7][0].strip()).split()[0]), delimiter=",", dtype=int
        )
        dic["y_n"] = np.array(1)
        dic["z_n"] = np.array(int((lol[7][0].strip()).split()[1]))
        for ent in ["x_n", "y_n", "z_n"]:
            if dic[f"{ent}"].size == 1:
                dic[f"{ent}"] = [dic[f"{ent}"]]
        dic["noCells"] = [sum(dic["x_n"]), sum(dic["y_n"]), sum(dic["z_n"])]
        dic["x_fac"] = 0
    else:
        dic["noCells"] = [int((lol[7][0].strip()).split()[j]) for j in range(2)]
        dic["noCells"].insert(1, 1)
        dic["x_fac"] = float((lol[7][0].strip()).split()[2])  # x-gridding coeff.
    dic["diameter"] = float((lol[8][0].strip()).split()[0])  # Well diameter [m]
    dic["jfactor"] = float(
        (lol[8][0].strip()).split()[1]
    )  # Well connection transmissibility factor [mD m]
    dic["removecells"] = int((lol[8][0].strip()).split()[2])  # Remove small cells
    dic["pressure"] = float((lol[9][0].strip()).split()[0]) / 1.0e5  # Convert to bar
    dic["temperature"] = float((lol[9][0].strip()).split()[1])
    dic["initialphase"] = int((lol[9][0].strip()).split()[2])
    dic["pvMult"] = float(lol[10][0])  # Pore volume multiplier [-]
    dic["perforations"] = [int((lol[11][0].strip()).split()[j]) for j in range(3)]
    dic["satnum"] = int((lol[12][0].strip()).split()[0])  # No. saturation regions
    dic["hysteresis"] = int((lol[12][0].strip()).split()[1])  # Hysteresis
    dic["econ"] = float((lol[12][0].strip()).split()[2])  # Econ
    dic["salt_props"] = [float((lol[13][0].strip()).split()[j]) for j in range(3)]
    dic["z_xy"] = str(lol[14][0])  # The function for the reservoir surface
    index = 17  # Increase this if more rows are added to the model parameters part
    dic["krwf"] = str(lol[index][0])  # Wetting rel perm saturation function [-]
    dic["krnf"] = str(lol[index + 1][0])  # Non-wetting rel perm saturation function [-]
    dic["pcwcf"] = str(lol[index + 2][0])  # Capillary pressure saturation function [Pa]
    index += 6
    return dic, index


def readthesecondpart(lol, dic, index):
    """
    Function to process the remaining lines in the configuration file

    Args:
        lol (list): List of lines read from the input file
        dic (dict): Global dictionary with required parameters
        inc (int): Number of line in the input file

    Returns:
        dic (dict): Global dictionary with new added parameters
    """
    for name in ["rock", "safu"]:
        dic[name] = []
    if dic["hysteresis"] == 1:
        dic["imbnum"] = 2
    else:
        dic["imbnum"] = 1
    for i in range(
        dic["imbnum"] * (dic["satnum"] + dic["perforations"][0])
    ):  # Saturation function values (divided by 1e5 to convert to bar)
        row = list((lol[index + i][0].strip()).split())
        dic["safu"].append(
            [
                float(row[1]),
                float(row[3]),
                float(row[5]),
                float(row[7]),
                float(row[9]) / 1.0e5,
                float(row[11]),
                float(row[13]),
                float(row[15]),
                float(row[17]),
                float(row[19]),
            ]
        )
    index += 3 + dic["imbnum"] * (dic["satnum"] + dic["perforations"][0])
    dic["thickness"] = []
    dic["nz_perlayer"] = []
    for i in range(dic["satnum"] + dic["perforations"][0]):  # Rock values
        row = list((lol[index + i][0].strip()).split())
        dic["rock"].append(
            [
                float(row[1]),
                float(row[3]),
                float(row[5]),
            ]
        )
        if i < dic["satnum"]:
            dic["thickness"].append(float(row[7]))
            if dic["model"] == "co2eor":
                dic["nz_perlayer"].append(int(row[9]))
    index += 3 + dic["satnum"] + dic["perforations"][0]
    column = []
    for i in range(len(lol) - index):
        if not lol[index + i]:
            break
        row = list((lol[index + i][0].strip()).split())
        column.append([float(row[j]) for j in range(5)])
    dic["inj"] = column
    return dic
