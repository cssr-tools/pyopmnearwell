# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Main script"""
import os
import argparse
from pyopmnearwell.utils.inputvalues import process_input
from pyopmnearwell.utils.runs import simulations, plotting
from pyopmnearwell.utils.writefile import reservoir_files
from pyopmnearwell.visualization.plotting import plot_results


def pyopmnearwell():
    """Main function"""
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
        default="ecl",
        help="Using the 'ecl' or 'opm' python package (ecl by default).",
    )
    parser.add_argument(
        "-c",
        "--compare",
        default="",
        help="Generate a common plot for the current folders ('' by default).",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    dic = {"pat": os.path.dirname(__file__)[:-5]}  # Path to the pyopmnearwell folder
    dic["exe"] = os.getcwd()  # Path to the folder of the input.txt file
    dic["fol"] = cmdargs["output"]  # Name for the output folder
    dic["plot"] = cmdargs["plotting"]  # The python package used for plotting
    dic["compare"] = cmdargs[
        "compare"
    ]  # If not empty, then the name of the compare plot (compare).

    # If the compare plot is generated, then we exit right afterwards
    if dic["compare"]:
        plot_results(dic)
        return
    file = cmdargs["input"]  # Name of the input file

    # Process the input file (open pyopmnearwell.utils.inputvalues to see the abbreviations meaning)
    dic = process_input(dic, file)

    # Make the output folders
    if not os.path.exists(f"{dic['exe']}/{dic['fol']}"):
        os.system(f"mkdir {dic['exe']}/{dic['fol']}")
    for fil in ["preprocessing", "jobs", "output", "postprocessing"]:
        if not os.path.exists(f"{dic['exe']}/{dic['fol']}/{fil}"):
            os.system(f"mkdir {dic['exe']}/{dic['fol']}/{fil}")
    os.chdir(f"{dic['exe']}/{dic['fol']}")

    # Write used opm related files
    reservoir_files(dic)

    # Run the model
    simulations(dic)

    # Make some useful plots after the studies
    plotting(dic)


def main():
    """Main function"""
    pyopmnearwell()
