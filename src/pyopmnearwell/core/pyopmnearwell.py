# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Main script"""
import argparse
import os
import pathlib
import warnings
from typing import Any

from pyopmnearwell.utils.inputvalues import process_input
from pyopmnearwell.utils.runs import plotting, simulations
from pyopmnearwell.utils.writefile import reservoir_files
from pyopmnearwell.visualization.plotting import plot_results


def pyopmnearwell():
    """Main function for the pyopmnearwell executable"""
    parser = argparse.ArgumentParser(
        description="Main script to run a near-well system with OPM Flow."
    )
    parser.add_argument(
        "-i",
        "--input",
        default="input.txt",
        help="The base name of the input file (input.txt by default).",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="The base name of the output folder (output by default).",
    )
    parser.add_argument(
        "-p",
        "--plotting",
        default="resdata",
        help="Using the 'resdata' or 'opm' python package or turn plotting 'off' "
        "(resdata by default).",
    )
    parser.add_argument(
        "-c",
        "--compare",
        default="",
        help="Generate a common plot for the current folders ('' by default).",
    )
    parser.add_argument(
        "-g",
        "--generate",
        default="all",
        help="Run the whole framework ('all'), only run flow ('flow'), "
        ", only write the deck and run flow together in the output folder ('single'), "
        "or only create plots ('plot') ('all' by default).",
    )
    parser.add_argument(
        "-v",
        "--vectors",
        default=1,
        help="Write cell values, i.e., EGRID, INIT, UNRST ('1' by default).",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="co2store",
        help=(
            "Simulated model (5th row in the configuration file). This is used "
            + "for the plotting compare method (it gets overwritten by the configuration file)"
            + "(co2store by default)."
        ),
    )
    parser.add_argument(
        "-z",
        "--zoom",
        default=20,
        help="xlim in meters for the zoomed in plots (20 by default)",
    )
    parser.add_argument(
        "-s",
        "--scale",
        default="normal",
        help="Scale for the x axis in the figures: 'normal' or 'log' ('normal' by default)",
    )
    parser.add_argument(
        "-w",
        "--warnings",
        default=0,
        help="Set to 1 to print warnings ('0' by default).",
    )
    parser.add_argument(
        "-l",
        "--latex",
        default=1,
        help="Set to 0 to not use LaTeX formatting ('1' by default).",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    if int(cmdargs["warnings"]) == 0:
        warnings.warn = lambda *args, **kwargs: None
    dic: dict[str, Any] = {
        "pat": os.path.split(os.path.dirname(__file__))[0]
    }  # Path to the pyopmnearwell folder
    dic["exe"] = os.getcwd()  # Path to the folder of the input.txt file
    dic["fol"] = cmdargs["output"].strip()  # Name for the output folder
    dic["plot"] = cmdargs["plotting"].strip()  # The python package used for plotting
    dic["model"] = cmdargs["model"].strip()  # Name of the simulated model
    dic["generate"] = cmdargs["generate"].strip()  # Parts of the workflow to run
    dic["write"] = int(cmdargs["vectors"])  # Write EGRID, INIT, and UNRST
    dic["scale"] = cmdargs["scale"].strip()  # Scale for the x axis: 'normal' or 'log'
    dic["zoom"] = float(cmdargs["zoom"])  # xlim in meters for the zoomed in plots
    dic["latex"] = int(cmdargs["latex"])  # LaTeX formatting
    dic["compare"] = cmdargs[
        "compare"
    ]  # If not empty, then the name of the compare plot (compare).
    # If the compare plot is generated, then we exit right afterwards
    if dic["compare"]:
        plot_results(dic)
        return

    file = cmdargs["input"].strip()  # Name of the input file
    dic["runname"] = pathlib.Path(file).stem

    # Process the input file (open pyopmnearwell.utils.inputvalues to see the
    # abbreviations meaning)
    dic = process_input(dic, file)

    # Make the output folders
    if not os.path.exists(os.path.join(dic["exe"], dic["fol"])):
        os.makedirs(os.path.join(dic["exe"], dic["fol"]))
    if dic["generate"] == "single":
        dic["fprep"] = f"{dic['exe']}/{dic['fol']}"
        dic["foutp"] = f"{dic['exe']}/{dic['fol']}"
    else:
        dic["fprep"] = f"{dic['exe']}/{dic['fol']}/preprocessing"
        dic["foutp"] = f"{dic['exe']}/{dic['fol']}/output"
        for fil in ["preprocessing", "jobs", "output", "postprocessing"]:
            if not os.path.exists(os.path.join(dic["exe"], dic["fol"], fil)):
                os.makedirs(os.path.join(dic["exe"], dic["fol"], fil))
    os.chdir(os.path.join(dic["exe"], dic["fol"]))

    if dic["generate"] in ["all", "flow", "single"]:
        # Write used opm related files
        reservoir_files(dic)

        # Run the model
        simulations(dic)

    # Make some useful plots after the studies
    if cmdargs["plotting"] != "off" and dic["generate"] in ["all", "plot"]:
        plotting(dic)


def main():
    """Main function"""
    pyopmnearwell()
