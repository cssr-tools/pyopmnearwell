# SPDX-FileCopyrightText: 2023-2026, NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Utility functions to run the studies"""

import os
import subprocess


def simulations(dic):
    """Run Flow"""
    if "foutp" not in dic:
        dic["foutp"] = f"{dic['fol']}/output"
    if "mode" not in dic:
        dic["mode"] = "all"
    os.makedirs(dic["foutp"], exist_ok=True)
    command = (
        f"{dic['flow']} --output-dir={dic['foutp']} "
        f"{dic['fprep']}/{dic['runname'].upper()}.DATA"
    )
    subprocess.run(
        command,
        cwd=dic["foutp"],
        shell=True,
        check=True,
    )
