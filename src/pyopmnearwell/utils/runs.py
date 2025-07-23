# SPDX-FileCopyrightText: 2023-2025, NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""
Utility functions to run the studies.
"""
import os


def simulations(dic):
    """
    Function to run Flow

    Args:
        dic (dict): Global dictionary with required parameters

    """
    if not "foutp" in dic:
        dic["foutp"] = f"{dic['fol']}/output"
    if not "mode" in dic:
        dic["mode"] = "all"
    os.chdir(dic["foutp"])
    os.system(
        f"{dic['flow']} --output-dir={dic['foutp']} "
        f"{dic['fprep']}/{dic['runname'].upper()}.DATA  & wait\n"
    )
