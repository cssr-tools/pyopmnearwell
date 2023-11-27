# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Utility functions to run the studies.
"""
import math as mt
import os

import numpy as np

from pyopmnearwell.visualization.plotting import plot_results


def simulations(dic):
    """
    Function to run Flow

    Args:
        dic (dict): Global dictionary with required parameters

    """
    os.chdir(f"{dic['exe']}/{dic['fol']}/output")
    os.system(
        f"{dic['flow']} --output-dir={dic['exe']}/{dic['fol']}/output "
        f"{dic['exe']}/{dic['fol']}/preprocessing/{dic['runname'].upper()}.DATA  & wait\n"
    )
    # We save few variables for the plotting methods
    np.save("xspace", dic["xcor"])
    np.save("zspace", dic["zcor"])
    np.save("ny", dic["noCells"][1])
    schedule = [0]
    for nrst in dic["inj"]:
        for _ in range(round(nrst[0] / nrst[1])):
            schedule.append(schedule[-1] + nrst[1] * 86400.0)
    np.save("schedule", schedule)
    np.save("radius", 0.5 * dic["diameter"])
    if dic["grid"] in ["cartesian2d", "cartesian"]:
        np.save("angle", 360.0)
    else:
        np.save("angle", dic["dims"][1])
    if dic["grid"] == "cartesian":
        np.save(
            "position", (dic["noCells"][0] - 1) * (mt.floor(dic["noCells"][0] / 2) + 1)
        )
    else:
        np.save("position", 0)


def plotting(dic):
    """
    Function to run the plotting.py file

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["folders"] = [dic["fol"]]
    os.system(
        f"cp {dic['pat']}/visualization/plotting.py {dic['exe']}/{dic['fol']}/jobs/"
    )
    os.chdir(f"{dic['exe']}/{dic['fol']}/postprocessing")
    plot_exe = [
        "python3",
        f"{dic['exe']}/{dic['fol']}/jobs/plotting.py",
        f"-f {dic['fol']}",
        f"-p {dic['plot']}",
        f"-m {dic['model']}",
        f"-s {dic['scale']}",
        f"-z {dic['zoom']}",
    ]
    print(" ".join(plot_exe))
    plot_results(dic)
