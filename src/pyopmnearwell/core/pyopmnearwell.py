# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Main script"""
import argparse
import os
import pathlib
import warnings
from typing import Any

from pyopmnearwell.utils.inputvalues import process_input
from pyopmnearwell.utils.runs import simulations
from pyopmnearwell.utils.writefile import reservoir_files


def pyopmnearwell():
    """Main function for the pyopmnearwell executable"""
    parser = argparse.ArgumentParser(
        description="Main script to run a near-well system with OPM Flow."
    )
    parser.add_argument(
        "-i",
        "--input",
        default="input.toml",
        help="The base name of the input file (input.toml by default).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="The base name of the output folder (output by default).",
    )
    parser.add_argument(
        "-m",
        "--mode",
        default="all",
        help="Run the whole framework ('all'), only generate the deck ('deck'), "
        "or only run flow ('flow'), or generate the deck and run flow in the same "
        "output folder ('single') ('all' by default).",
    )
    parser.add_argument(
        "-v",
        "--vectors",
        default=1,
        help="Write cell values, i.e., EGRID, INIT, UNRST ('1' by default).",
    )
    parser.add_argument(
        "-w",
        "--warnings",
        default=0,
        help="Set to 1 to print warnings ('0' by default).",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    if int(cmdargs["warnings"]) == 0:
        warnings.warn = lambda *args, **kwargs: None
    dic: dict[str, Any] = {
        "pat": os.path.split(os.path.dirname(__file__))[0]
    }  # Path to the pyopmnearwell folder
    dic["fol"] = os.path.abspath(cmdargs["output"])  # Name for the output folder
    dic["mode"] = cmdargs["mode"].strip()  # Parts of the workflow to run
    dic["write"] = int(cmdargs["vectors"])  # Write EGRID, INIT, and UNRST
    file = cmdargs["input"].strip()  # Name of the input file
    dic["runname"] = pathlib.Path(file).stem
    dic = process_input(dic, file)  # Read the toml configuration file

    # Make the output folders
    if not os.path.exists(dic["fol"]):
        os.makedirs(dic["fol"])
    if dic["mode"] == "single":
        dic["fprep"] = dic["fol"]
        dic["foutp"] = dic["fol"]
    else:
        dic["fprep"] = f"{dic['fol']}/preprocessing"
        dic["foutp"] = f"{dic['fol']}/output"
    os.chdir(dic["fol"])

    if dic["mode"] in ["all", "deck", "single"]:
        # Write used opm related files
        if not os.path.exists(dic["fprep"]):
            os.makedirs(dic["fprep"])
        reservoir_files(dic)
    if dic["mode"] in ["all", "flow", "single"]:
        # Run the model
        if not os.path.exists(dic["foutp"]):
            os.makedirs(dic["foutp"])
        simulations(dic)


def main():
    """Main function"""
    pyopmnearwell()
