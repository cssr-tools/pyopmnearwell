# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to return the interpolated pressure
"""

import argparse
import csv
import os

import numpy as np
from scipy.interpolate import interp1d


def main():
    """Get the pressure at a given distance"""
    parser = argparse.ArgumentParser(description="Main script to plot the results")
    parser.add_argument(
        "-d",
        "--distance",
        default=1.0,
        help="The distance from the well to get the pressure (1 meter by default).",
    )
    parser.add_argument(
        "-n",
        "--name",
        default="output",
        help="The name of the folder to the studies.",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    folders = [cmdargs["name"].strip()]
    distance = float(cmdargs["distance"])
    for i, study in enumerate(folders):
        data = []
        table = os.getcwd() + "/" + study + "/postprocessing/pressure.csv"
        with open(table, "r", encoding="utf8") as file:
            for i, row in enumerate(csv.reader(file, delimiter=" ")):
                if i == 0:
                    q_rate = float(row[2])
                if i == 1:
                    p_well = float(row[2])
                if i < 6:
                    continue
                data.append(row)
    xvalue = np.array([float(row[0]) for row in data])
    yvalue = np.array([float(row[1]) for row in data])
    interp_func = interp1d(xvalue, yvalue, fill_value="extrapolate")
    print(f"Distance : {distance} [m]")
    print(f"Pressure : {interp_func(distance)} [bar]")
    # pylint: disable-next=possibly-used-before-assignment
    print(f"WI computed : {q_rate/(p_well-interp_func(distance))} [kg/(Bar day)]")


if __name__ == "__main__":
    main()
