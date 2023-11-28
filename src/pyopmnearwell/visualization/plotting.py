# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to plot OPM Flow results
"""

import argparse
import os
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from pyopmnearwell.visualization.reading import read_simulations
from pyopmnearwell.visualization.additional_plots import final_time_maps, saltprec_plots

font = {"family": "normal", "weight": "normal", "size": 13}
matplotlib.rc("font", **font)
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "monospace",
        "legend.columnspacing": 0.9,
        "legend.handlelength": 1.5,
        "legend.fontsize": 12,
        "lines.linewidth": 4,
        "axes.titlesize": 13,
        "axes.grid": True,
        "figure.figsize": (10, 5),
    }
)


def main():
    """Postprocessing"""
    parser = argparse.ArgumentParser(description="Main script to plot the results")
    parser.add_argument(
        "-f",
        "--folder",
        default="output",
        help="The folder to the studies.",
    )
    parser.add_argument(
        "-p",
        "--plot",
        default="ecl",
        help="Using the 'ecl' or 'opm' python package.",
    )
    parser.add_argument(
        "-c",
        "--compare",
        default="",
        help="Generate a common plot for the current folders.",
    )
    parser.add_argument(
        "-m",
        "--model",
        default="co2store",
        help="Simulated model (5th word in the configuration file).",
    )
    parser.add_argument(
        "-z",
        "--zoom",
        default=20,
        help="xlim for the zoomed in plots",
    )
    parser.add_argument(
        "-s",
        "--scale",
        default="normal",
        help="Normal or log scale for the x axis",
    )
    cmdargs = vars(parser.parse_known_args()[0])
    dic = {"folders": [cmdargs["folder"].strip()]}
    dic["plot"] = cmdargs["plot"].strip()  # Using ecl or opm
    dic["compare"] = cmdargs["compare"].strip()  # Name of the compare plot
    dic["model"] = cmdargs["model"].strip()  # Name of the simulated model
    dic["scale"] = cmdargs["scale"].strip()  # Scale for the x axis: 'normal' or 'log'
    dic["zoom"] = float(cmdargs["zoom"])  # xlim in meters for the zoomed in plots
    dic["exe"] = os.getcwd()  # Path to the folder of the input.txt file
    plot_results(dic)


def plot_results(dic):
    """
    Function to plot the 2D maps/1D projections for the different quantities

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["sat_thr"] = 5e-2  # Threshold for the non-wetting saturation
    dic["rock"] = ["satnum", "permeability", "porosity"]
    dic["rock_units"] = ["[-]", "mD", "[-]"]
    dic["quantity"] = ["pressure", "saturation"]
    dic["units"] = ["[Bar]", "[-]"]
    dic["labels"] = ["Pressure", "Non-wetting saturation"]
    if dic["model"] == "saltprec":
        dic["quantity"].append("salt")
        dic["quantity"].append("permfact")
        dic["units"].append("[-]")
        dic["units"].append("[-]")
        dic["labels"].append("Precipitated salt saturation")
        dic["labels"].append("Permeability multiplier")
    dic["linestyle"] = [
        (0, ()),
        "--",
        (0, (1, 1)),
        "-.",
        (0, (1, 10)),
        (0, (1, 1)),
        (5, (10, 3)),
        (0, (5, 10)),
        (0, (5, 5)),
        (0, (5, 1)),
        (0, (3, 10, 1, 10)),
        (0, (3, 5, 1, 5)),
        (0, (3, 1, 1, 1)),
        (0, (3, 5, 1, 5, 1, 5)),
        (0, (3, 10, 1, 10, 1, 10)),
        (0, (3, 1, 1, 1, 1, 1)),
    ]
    dic["colors"] = [
        "#1f77b4",
        "#ff7f0e",
        "#2ca02c",
        "#d62728",
        "#9467bd",
        "#8c564b",
        "#e377c2",
        "#7f7f7f",
        "#bcbd22",
        "#17becf",
    ]

    if dic["compare"]:
        dic["where"] = "compare/"
        dic["folders"] = sorted(
            [name for name in os.listdir(".") if os.path.isdir(name)]
        )
        if "compare" not in dic["folders"]:
            os.system(f"mkdir {dic['exe']}/compare")
        else:
            os.system(f"rm -rf {dic['exe']}/compare")
            os.system(f"mkdir {dic['exe']}/compare")
            dic["folders"].remove("compare")
    else:
        dic["where"] = "."
    dic = read_simulations(dic)
    dic = capillary_pressure(dic)
    dic = over_time_well_injectivity(dic)
    dic = over_time_max_distance(dic)
    if dic["model"] == "h2store":
        return
    dic = over_time_layers(dic)
    dic = evaluate_projections(dic)
    over_time_well_cell(dic)
    final_time_projections_bottom(dic)
    final_time_projections_layered(dic)
    final_time_projections_norms(dic)
    final_time_projections_max(dic)
    if dic["model"] == "saltprec" and not dic["compare"]:
        saltprec_plots(dic)
    if dic["plot"] == "ecl":
        all_injectivities(dic)
    # if dic["connections"]:
    #     connections_injectivities(dic)
    if dic["compare"]:
        return
    final_time_maps(dic)


def connections_injectivities(dic):
    """
    Function to plot the rates over the wells BHP
    """
    quantites = ["rate", "productivity"]
    units = [
        "Rate [sm$^3$/day]",
        "Productivity [sm$^3$/(Bar day)]",
    ]
    for i, quantity in enumerate(quantites):
        dic["fig"], dic["axis"] = plt.subplots()
        for study in dic["folders"]:
            for k in range(dic[f"{study}_nz"]):
                dic[f"{study}_rate_plot"] = []
                dic[f"{study}_productivity_plot"] = []
                for nrst in dic[f"{study}_smsp_rst"]:
                    dic[f"{study}_rate_plot"].append(
                        dic[f"{study}_smsp"][f"CGIR:INJ0:1,1,{k+1}"].values[nrst]
                    )
                    dic[f"{study}_productivity_plot"].append(
                        dic[f"{study}_smsp"][f"CPI:INJ0:1,1,{k+1}"].values[nrst]
                    )
                dic["axis"].plot(
                    dic[f"{study}_report_time"],
                    dic[f"{study}_{quantity}_plot"],
                    label=f"1,1,{k+1}",
                )
        dic["axis"].set_ylabel(units[i])
        dic["axis"].set_xlabel("Time")
        dic["axis"].legend()
        dic["axis"].xaxis.set_tick_params(size=6, rotation=45)
        dic["fig"].savefig(f"{dic['where']}/c_{quantity}.png", bbox_inches="tight")

        plt.close()


def all_injectivities(dic):
    """
    Function to plot the rates over the wells BHP
    """
    quantites = ["pressure", "rate", "injectivity"]
    units = [
        "BHP [Bar]",
        "Rate [sm3/day]",
        "Injectivity [sm3/(Bar day)]",
    ]
    for i, quantity in enumerate(quantites):
        dic["fig"], dic["axis"] = plt.subplots()
        for study in dic["folders"]:
            for well in dic[f"{study}_smsp"].wells():
                dic[f"{study}_pressure_plot"] = []
                dic[f"{study}_rate_plot"] = []
                dic[f"{study}_injectivity_plot"] = []
                for nrst in dic[f"{study}_smsp_rst"]:
                    dic[f"{study}_pressure_plot"].append(
                        dic[f"{study}_smsp"][f"WBHP:{well}"].values[nrst]
                    )
                    dic[f"{study}_rate_plot"].append(
                        dic[f"{study}_smsp"][f"WGIR:{well}"].values[nrst]
                    )
                    dic[f"{study}_injectivity_plot"].append(
                        dic[f"{study}_rate_plot"][-1]
                        / dic[f"{study}_pressure_plot"][-1]
                    )
                dic["axis"].plot(
                    dic[f"{study}_report_time"],
                    dic[f"{study}_{quantity}_plot"],
                    label=f"{study}",
                )
        dic["axis"].set_ylabel(units[i])
        dic["axis"].set_xlabel("Time")
        dic["axis"].legend()
        dic["axis"].xaxis.set_tick_params(size=6, rotation=45)
        dic["fig"].savefig(f"{dic['where']}/w_{quantity}.png", bbox_inches="tight")

        plt.close()


def capillary_pressure(dic):
    """
    Function to plot the capillary pressure function
    """
    fig, axis = plt.subplots()
    for i, study in enumerate(dic["folders"]):
        data = []
        data.append([])
        table = dic["exe"] + "/" + study + "/preprocessing/TABLES.INC"
        with open(table, "r", encoding="utf8") as file:
            for row in csv.reader(file, delimiter=" "):
                if row[0] == "SGOF":
                    kind = 0
                    col = 3
                    axis.set_xlabel("Non-wetting saturation [-]")
                else:
                    kind = 1
                    col = 2
                    axis.set_xlabel("Wetting saturation [-]")
                break
        data = read_table(table, kind)
        for j in range(len(data) - 1):
            axis.plot(
                [float(row[0]) for row in data[j]],
                [1e5 * float(row[col]) for row in data[j]],
                label=f"{study}",
                color=dic["colors"][i % len(dic["colors"])],
                linestyle=dic["linestyle"][j % len(dic["linestyle"])],
            )
    xvalue = np.array([float(row[0]) for row in data[0]])
    yvalue = np.array([float(row[col]) for row in data[0]])
    dic["cp_func"] = interp1d(xvalue, yvalue, fill_value="extrapolate")
    if yvalue[0] > 0:
        axis.set_yscale("log")
    axis.set_ylabel("Capillary pressure [Pa]")
    axis.legend()
    axis.set_xlim([0, 1])
    fig.savefig(f"{dic['where']}/capillary_pressure.png", bbox_inches="tight")
    return dic


def read_table(table, kind):
    """
    Function to read the capillary pressure table

    Args:
        table (str): Name of the table file
        kind (int): Type of the format of the table

    Returns:
        data (list): List with the saturation and pressure values

    """
    data = []
    data.append([])
    indc = 0
    with open(table, "r", encoding="utf8") as file:
        for row in csv.reader(file, delimiter=" "):
            if kind == 1:
                if row[0] == "SWFN" or indc == 1:
                    if indc == 0:
                        indc = 1
                    elif row[0] == "/":
                        data.append([])
                        continue
                    else:
                        data[-1].append(row)
            else:
                if row[0] == "SGOF" or indc == 1:
                    if indc == 0:
                        indc = 1
                    elif row[0] == "/":
                        data.append([])
                        continue
                    else:
                        data[-1].append(row)
    return data


def evaluate_projections(dic):
    """
    Function to plot the 1D projected quantities along the z direction
    """
    dic["projection"] = [
        "bottom_cells",
        "middle_cells",
        "top_cells",
        "max",
        "min",
        "mean",
    ]
    dic["well_cell"] = [
        "wc_max",
        "wc_min",
        "wc_mean",
    ]
    for quantity in dic["quantity"]:
        for study in dic["folders"]:
            for projection in dic["projection"]:
                dic[f"{study}_{quantity}_{projection}"] = []
            for well_cell in dic["well_cell"]:
                dic[f"{study}_{quantity}_{well_cell}"] = []
            for i in range(len(dic[f"{study}_xmidpoints"])):
                temp = np.array(
                    [
                        dic[f"{study}_{quantity}_array"][-1][k]
                        for k in range(
                            i,
                            dic[f"{study}_nx"] * dic[f"{study}_nz"],
                            len(dic[f"{study}_xmidpoints"]),
                        )
                    ]
                )
                dic[f"{study}_{quantity}_top_cells"].append(temp[0])
                dic[f"{study}_{quantity}_bottom_cells"].append(temp[-1])
                dic[f"{study}_{quantity}_middle_cells"].append(
                    temp[round(0.5 * dic[f"{study}_nz"])]
                )
                dic[f"{study}_{quantity}_max"].append(temp.max())
                dic[f"{study}_{quantity}_min"].append(temp.min())
                dic[f"{study}_{quantity}_mean"].append(temp.mean())
            for nrst in range(len(dic[f"{study}_rst"].report_steps)):
                temp = np.array(
                    [
                        dic[f"{study}_{quantity}_array"][nrst][k]
                        for k in range(
                            dic[f"{study}_wellid"],
                            dic[f"{study}_nx"]
                            * dic[f"{study}_ny"]
                            * dic[f"{study}_nz"],
                            dic[f"{study}_ny"]
                            * max(dic[f"{study}_nx"], dic[f"{study}_ny"]),
                        )
                    ]
                )
                dic[f"{study}_{quantity}_wc_max"].append(temp.max())
                dic[f"{study}_{quantity}_wc_min"].append(temp.min())
                dic[f"{study}_{quantity}_wc_mean"].append(temp.mean())
    return dic


def final_time_projections_bottom(dic):
    """
    Function to plot the 1D projected quantities along the z direction
    """
    for j, quantity in enumerate(dic["quantity"]):
        fig, axis = plt.subplots()
        nlines = 1
        for ncolor, study in enumerate(dic["folders"]):
            if dic[f"{study}_nz"] > 1:
                dic["names"] = ["Bottom layer"]
            else:
                dic["names"] = ["Simulation"]
            if dic[f"{study}_wellid"] == 0:
                for k, projection in enumerate(dic["projection"][:nlines]):
                    axis.plot(
                        dic[f"{study}_xmidpoints"],
                        dic[f"{study}_{quantity}_{projection}"],
                        label=f"{study}",
                        color=dic["colors"][ncolor % len(dic["colors"])],
                        linestyle=dic["linestyle"][k % len(dic["linestyle"])],
                    )
            else:
                axis.plot(
                    dic[f"{study}_xmidpoints"],
                    [
                        dic[f"{study}_{quantity}_array"][-1][
                            dic[f"{study}_wellid"] + i * (2 * dic[f"{study}_nx"] - 1)
                        ]
                        for i in range(len(dic[f"{study}_xmidpoints"]))
                    ],
                    label=f"{dic['names'][0]} ({study})",
                    color=dic["colors"][ncolor % len(dic["colors"])],
                )
            if quantity == "pressure" and dic[f"{study}_nz"] < 2:
                npoints = 10000
                axis.plot(
                    [
                        r * dic[f"{study}_xmidpoints"][-1] / npoints
                        for r in range(1, npoints + 1)
                    ],
                    [
                        (
                            dic[f"{study}_pressure_array"][0][-1]
                            + 1e-5
                            * (
                                dic[f"{study}_mu"]
                                * 1e-3
                                * (
                                    (360.0 / dic[f"{study}_angle"])
                                    * dic[f"{study}_Qrho"]
                                    / (86400.0)
                                )
                                / (
                                    2
                                    * 3.1416
                                    * dic[f"{study}_permeability_array"][-1][0]
                                    * 0.986923e-15
                                    * dic[f"{study}_zmz"][-1]
                                )
                            )
                            * np.log(
                                dic[f"{study}_xmidpoints"][-1] / dic[f"{study}_radius"]
                            )
                            - 1e-5
                            * (
                                dic[f"{study}_mu"]
                                * 1e-3
                                * (
                                    (360.0 / dic[f"{study}_angle"])
                                    * dic[f"{study}_Qrho"]
                                    / (86400.0)
                                )
                                / (
                                    2
                                    * 3.1416
                                    * dic[f"{study}_permeability_array"][-1][0]
                                    * 0.986923e-15
                                    * dic[f"{study}_zmz"][-1]
                                )
                            )
                            * np.log(
                                (r * dic[f"{study}_xmidpoints"][-1] / npoints)
                                / dic[f"{study}_radius"]
                            )
                        )
                        for r in range(1, npoints + 1)
                    ],
                    label=f"Analytical solution ({study})",
                    color="k",
                    linestyle=dic["linestyle"][-1],
                )
                with open(
                    f"{dic['where']}/pressure.csv",
                    "w",
                    encoding="utf8",
                ) as file:
                    file.write(f"q = {dic[f'{study}_Q']:.6E}" + " [kg/day]\n")
                    file.write(f"pw = {dic[f'{study}_well_pressure'][-1]:.6E} [Bar]\n")
                    file.write(
                        f"p0 = {dic[f'{study}_pressure_array'][-1][dic[f'{study}_wellid']]:.6E}"
                        + " [Bar]\n"
                    )
                    file.write(f"WI = {dic[f'{study}_WI']:.6E} [kg/(Bar day)]\n")
                    file.write(f"T = {dic[f'{study}_T']:.6E} [mD m]\n")
                    file.write("Distance [m] Pressure [Bar]\n")
                    for distance, pressure in zip(
                        dic[f"{study}_xmidpoints"][:-1],
                        dic[f"{study}_pressure_bottom_cells"][:-1],
                    ):
                        file.write(f"{distance:.3E} {pressure:.3E}\n")
                    file.write(
                        f"{dic[f'{study}_xmidpoints'][-1]:.3E} "
                        + f"{dic[f'{study}_pressure_bottom_cells'][-1]:.3E}"
                    )
        finish_plotting(dic, axis, j, fig, quantity)


def finish_plotting(dic, axis, j, fig, quantity):
    """
    Function to finish the final_time_projections_bottom method
    """
    axis.set_xlabel("Distance from wellbore [m]")
    axis.set_ylabel(f"{dic['labels'][j]} {dic['units'][j]}")
    axis.set_title("Bottom cells of the reservoir")
    axis.legend()
    if dic["scale"] == "log":
        axis.set_xscale("log")
    if quantity == "permfact":
        axis.set_ylim([0, 1])
    fig.savefig(
        f"{dic['where']}/{quantity}_1D_single_layer_x{dic['scale']}.png",
        bbox_inches="tight",
    )
    if dic["scale"] == "log":
        axis.set_xlim(right=dic["zoom"])
    else:
        axis.set_xlim([0, dic["zoom"]])
    fig.savefig(
        f"{dic['where']}/{quantity}_1D_single_layer_zoom{dic['zoom']}_x{dic['scale']}.png",
        bbox_inches="tight",
    )
    plt.close()


def final_time_projections_layered(dic):
    """
    Function to plot the 1D projected quantities along the z direction
    """
    for j, quantity in enumerate(dic["quantity"]):
        fig, axis = plt.subplots()
        for ncolor, study in enumerate(dic["folders"]):
            if dic[f"{study}_nz"] > 1:
                nlines = 3
                dic["names"] = ["Bottom layer", "Mid layer", "Upper layer"]
            else:
                nlines = 1
                dic["names"] = ["Simulation"]
            if dic[f"{study}_wellid"] == 0:
                for k, projection in enumerate(dic["projection"][:nlines]):
                    axis.plot(
                        dic[f"{study}_xmidpoints"],
                        dic[f"{study}_{quantity}_{projection}"],
                        label=f"{dic['names'][k]} ({study})",
                        color=dic["colors"][ncolor % len(dic["colors"])],
                        linestyle=dic["linestyle"][k % len(dic["linestyle"])],
                    )
            else:
                axis.plot(
                    dic[f"{study}_xmidpoints"],
                    [
                        dic[f"{study}_{quantity}_array"][-1][
                            dic[f"{study}_wellid"] + i * (2 * dic[f"{study}_nx"] - 1)
                        ]
                        for i in range(len(dic[f"{study}_xmidpoints"]))
                    ],
                    label=f"{dic['names'][0]} ({study})",
                    color=dic["colors"][ncolor % len(dic["colors"])],
                )
        axis.set_xlabel("Distance from wellbore [m]")
        axis.set_ylabel(f"{dic['labels'][j]} {dic['units'][j]}")
        axis.legend()
        if dic["scale"] == "log":
            axis.set_xscale("log")
        if quantity == "permfact":
            axis.set_ylim([0, 1])
        fig.savefig(
            f"{dic['where']}/{quantity}_1D_layered_x{dic['scale']}.png",
            bbox_inches="tight",
        )
        if dic["scale"] == "log":
            axis.set_xlim(right=dic["zoom"])
        else:
            axis.set_xlim([0, dic["zoom"]])
        fig.savefig(
            f"{dic['where']}/{quantity}_1D_layered_zoom{dic['zoom']}_x{dic['scale']}.png",
            bbox_inches="tight",
        )
        plt.close()


def over_time_well_cell(dic):
    """
    Function to plot the 1D normed quantities along the z direction

    Args:
        dic (dict): Global dictionary with required parameters

    """
    for j, quantity in enumerate(dic["quantity"]):
        fig, axis = plt.subplots()
        figm, axism = plt.subplots()
        for i, study in enumerate(dic["folders"]):
            if dic[f"{study}_nz"] > 1:
                nlines = -3
                dic["names"] = ["Max", "Min", "Mean"]
            else:
                nlines = -1
                dic["names"] = ["Simulation"]
            for k, well_cell in enumerate(dic["well_cell"][nlines:]):
                axis.plot(
                    dic[f"{study}_report_time"],
                    dic[f"{study}_{quantity}_{well_cell}"],
                    label=f"{dic['names'][k]} ({study})",
                    color=dic["colors"][i % len(dic["colors"])],
                    linestyle=dic["linestyle"][k % len(dic["linestyle"])],
                )
            axism.plot(
                dic[f"{study}_report_time"],
                dic[f"{study}_{quantity}_wc_mean"],
                label=f"{study}",
                color=dic["colors"][i % len(dic["colors"])],
            )
        axis.set_xlabel("Time")
        axis.set_ylabel(f"{dic['labels'][j]} {dic['units'][j]}")
        axis.legend()
        axis.set_title("Along the well cells (x=0)")
        axis.xaxis.set_tick_params(size=6, rotation=45)
        if quantity == "permfact":
            axis.set_ylim([0, 1])
        fig.savefig(f"{dic['where']}/well_cell_{quantity}.png", bbox_inches="tight")
        axism.set_xlabel("Time")
        axism.set_ylabel(f"{dic['labels'][j]} {dic['units'][j]}")
        axism.set_title("Mean along the well cells (x=0)")
        axism.legend()
        axism.xaxis.set_tick_params(size=6, rotation=45)
        if quantity == "permfact":
            axism.set_ylim([0, 1])
        figm.savefig(
            f"{dic['where']}/well_cell_{quantity}_mean.png", bbox_inches="tight"
        )
        plt.close()


def final_time_projections_norms(dic):
    """
    Function to plot the 1D normed quantities along the z direction

    Args:
        dic (dict): Global dictionary with required parameters

    """
    for j, quantity in enumerate(dic["quantity"]):
        fig, axis = plt.subplots()
        for ncolor, study in enumerate(dic["folders"]):
            if dic[f"{study}_nz"] > 1:
                nlines = -3
                dic["names"] = ["Max", "Min", "Mean"]
            else:
                nlines = -1
                dic["names"] = ["Simulation"]
            if dic[f"{study}_wellid"] == 0:
                for k, projection in enumerate(dic["projection"][nlines:]):
                    axis.plot(
                        dic[f"{study}_xmidpoints"],
                        dic[f"{study}_{quantity}_{projection}"],
                        label=f"{dic['names'][k]} ({study})",
                        color=dic["colors"][ncolor % len(dic["colors"])],
                        linestyle=dic["linestyle"][k % len(dic["linestyle"])],
                    )
            else:
                axis.plot(
                    dic[f"{study}_xmidpoints"],
                    [
                        dic[f"{study}_{quantity}_array"][-1][
                            dic[f"{study}_wellid"] + i * (2 * dic[f"{study}_nx"] - 1)
                        ]
                        for i in range(len(dic[f"{study}_xmidpoints"]))
                    ],
                    label=f"{dic['names'][0]} ({study})",
                    color=dic["colors"][ncolor % len(dic["colors"])],
                )
        axis.set_xlabel("Distance from wellbore [m]")
        axis.set_ylabel(f"{dic['labels'][j]} {dic['units'][j]}")
        axis.legend()
        if dic["scale"] == "log":
            axis.set_xscale("log")
        if quantity == "permfact":
            axis.set_ylim([0, 1])
        fig.savefig(
            f"{dic['where']}/{quantity}_1D_norms_x{dic['scale']}.png",
            bbox_inches="tight",
        )
        if dic["scale"] == "log":
            axis.set_xlim(right=dic["zoom"])
        else:
            axis.set_xlim([0, dic["zoom"]])
        fig.savefig(
            f"{dic['where']}/{quantity}_1D_norms_zoom{dic['zoom']}_x{dic['scale']}.png",
            bbox_inches="tight",
        )
        plt.close()


def final_time_projections_max(dic):
    """
    Function to plot the 1D normed quantities along the z direction

    Args:
        dic (dict): Global dictionary with required parameters

    """
    for j, quantity in enumerate(dic["quantity"]):
        fig, axis = plt.subplots()
        for ncolor, study in enumerate(dic["folders"]):
            if dic[f"{study}_nz"] > 1:
                dic["names"] = ["Max"]
            else:
                dic["names"] = ["Simulation"]
            if dic[f"{study}_wellid"] == 0:
                for k, projection in enumerate([dic["projection"][3]]):
                    axis.plot(
                        dic[f"{study}_xmidpoints"],
                        dic[f"{study}_{quantity}_{projection}"],
                        label=f"{study}",
                        color=dic["colors"][ncolor % len(dic["colors"])],
                        linestyle=dic["linestyle"][k % len(dic["linestyle"])],
                    )
            else:
                axis.plot(
                    dic[f"{study}_xmidpoints"],
                    [
                        dic[f"{study}_{quantity}_array"][-1][
                            dic[f"{study}_wellid"] + i * (2 * dic[f"{study}_nx"] - 1)
                        ]
                        for i in range(len(dic[f"{study}_xmidpoints"]))
                    ],
                    label=f"{study}",
                    color=dic["colors"][ncolor % len(dic["colors"])],
                )
        axis.set_xlabel("Distance from wellbore [m]")
        axis.set_ylabel(f"{dic['labels'][j]} {dic['units'][j]}")
        axis.set_title("Maximum value along the height of the reservoir")
        axis.legend()
        if dic["scale"] == "log":
            axis.set_xscale("log")
        if quantity == "permfact":
            axis.set_ylim([0, 1])
        fig.savefig(
            f"{dic['where']}/{quantity}_1D_max_x{dic['scale']}.png", bbox_inches="tight"
        )
        if dic["scale"] == "log":
            axis.set_xlim(right=dic["zoom"])
        else:
            axis.set_xlim([0, dic["zoom"]])
        fig.savefig(
            f"{dic['where']}/{quantity}_1D_max_zoom{dic['zoom']}_x{dic['scale']}.png",
            bbox_inches="tight",
        )
        plt.close()


def over_time_max_distance(dic):
    """
    Max horizontal distance from the well to the non-wetting plume

    Args:
        dic (dict): Global dictionary with required parameters

    """

    dic["fig"], dic["axis"] = [], []
    fig, axis = plt.subplots()
    dic["fig"].append(fig)
    dic["axis"].append(axis)
    for j, study in enumerate(dic["folders"]):
        dic["dx_half_size"] = dic[f"{study}_xmidpoints"][0]
        dic[f"{study}_indicator_plot"] = []
        for nrst in range(len(dic[f"{study}_rst"].report_steps)):
            i_max_ind = 0
            for i in range(dic[f"{study}_nz"]):
                temp = np.array(
                    dic[f"{study}_indicator_array"][nrst][
                        dic[f"{study}_nx"] * i : (i + 1) * dic[f"{study}_nx"]
                    ]
                )
                if np.where(temp)[0].size > 0:
                    i_max_ind = max(i_max_ind, np.where(temp)[0][-1])
            closest_distance = (
                dic[f"{study}_xmidpoints"][i_max_ind] - dic["dx_half_size"]
            )
            dic[f"{study}_indicator_plot"].append(closest_distance)
        dic["axis"][-1].plot(
            dic[f"{study}_report_time"],
            dic[f"{study}_indicator_plot"],
            color=dic["colors"][j % len(dic["colors"])],
            label=f"{study}",
        )
    dic["axis"][-1].set_ylabel("Plume distance to well [m]")
    dic["axis"][-1].set_xlabel("Time")
    dic["axis"][-1].legend()
    dic["axis"][-1].xaxis.set_tick_params(size=6, rotation=45)
    dic["fig"][-1].savefig(
        f"{dic['where']}/distance_from_well.png", bbox_inches="tight"
    )
    plt.close()

    return dic


def over_time_well_injectivity(dic):
    """
    Function to plot the well injectivity

    Args:
        dic (dict): Global dictionary with required parameters

    """

    quantites = ["injectivity", "ratew", "raten", "pressure", "pi"]
    units = [
        "Injectivity [kg/(Bar day)]",
        "Rate [kg/day]",
        "Rate [kg/day]",
        "Pressure [Bar]",
        "Productivity [sm$^3$/(Bar day)]",
    ]
    for i, quantity in enumerate(quantites):
        dic["fig"], dic["axis"] = plt.subplots()
        for k, study in enumerate(dic["folders"]):
            dic[f"{study}_xmx"] = np.load(
                dic["exe"] + "/" + study + "/output/xspace.npy"
            )
            dic[f"{study}_zmz"] = np.load(
                dic["exe"] + "/" + study + "/output/zspace.npy"
            )
            dic[f"{study}_ny"] = np.load(dic["exe"] + "/" + study + "/output/ny.npy")
            dic[f"{study}_nx"] = len(dic[f"{study}_xmx"]) - 1
            dic[f"{study}_nz"] = len(dic[f"{study}_zmz"]) - 1
            dic[f"{study}_xmidpoints"] = 0.5 * (
                dic[f"{study}_xmx"][1:] + dic[f"{study}_xmx"][:-1]
            )
            dic[f"{study}_injectivity_plot"] = []
            dic[f"{study}_raten_plot"] = []
            dic[f"{study}_ratew_plot"] = []
            dic[f"{study}_pressure_plot"] = []
            dic[f"{study}_well_pressure_plot"] = []
            dic[f"{study}_pi_plot"] = []
            for j, nrst in enumerate(dic[f"{study}_smsp_rst"][1:]):
                ratew = dic[f"{study}_injection_ratew"][nrst] * dic[f"{study}_rhow_ref"]
                raten = dic[f"{study}_injection_raten"][nrst] * dic[f"{study}_rhon_ref"]
                well_pressure = dic[f"{study}_well_pressure"][nrst]
                dic[f"{study}_pi_plot"].append(dic[f"{study}_well_pi"][nrst])
                if well_pressure == 0:
                    ratew = 0
                    raten = 0
                if well_pressure == 0:
                    dic[f"{study}_injectivity_plot"].append(0)
                else:
                    dic[f"{study}_injectivity_plot"].append(
                        max(raten, ratew)
                        / (
                            well_pressure
                            - (
                                dic[f"{study}_pressure_array"][j + 1][
                                    dic[f"{study}_wellid"]
                                ]
                                - dic["cp_func"](
                                    1.0
                                    - dic[f"{study}_saturation_array"][j + 1][
                                        dic[f"{study}_wellid"]
                                    ]
                                )
                            )
                        )
                    )
                dic[f"{study}_ratew_plot"].append(ratew)
                dic[f"{study}_raten_plot"].append(raten)
                dic[f"{study}_pressure_plot"].append(well_pressure)
            if quantity == "pressure":
                dic["axis"].plot(
                    dic[f"{study}_rst_seconds"][1:],
                    dic[f"{study}_{quantity}_plot"],
                    label=f"well ({study})",
                    color=dic["colors"][k % len(dic["colors"])],
                )
                dic["axis"].plot(
                    dic[f"{study}_rst_seconds"],
                    [
                        value[dic[f"{study}_wellid"]] - dic["cp_func"](1)
                        for value in dic[f"{study}_pressure_array"]
                    ],
                    label=f"cell ({study})",
                    color=dic["colors"][k % len(dic["colors"])],
                    linestyle="dotted",
                )
                dic["axis"].set_xlabel("Time [s]")
            else:
                dic["axis"].plot(
                    dic[f"{study}_report_time"][1:],
                    dic[f"{study}_{quantity}_plot"],
                    label=f"{study}",
                    color=dic["colors"][k % len(dic["colors"])],
                )
                dic["axis"].set_xlabel("Time")
        dic["axis"].set_ylabel(units[i])
        dic["axis"].legend()
        dic["axis"].xaxis.set_tick_params(size=6, rotation=45)
        dic["fig"].savefig(f"{dic['where']}/well_{quantity}.png", bbox_inches="tight")

        plt.close()

    return dic


def over_time_layers(dic):
    """
    Function to plot the well injectivity

    Args:
        dic (dict): Global dictionary with required parameters

    """

    dic["names"] = ["Upper layer", "Mid layer", "Bottom layer"]
    for i, quantity in enumerate(dic["quantity"]):
        dic["fig"], dic["axis"] = plt.subplots()
        for j, study in enumerate(dic["folders"]):
            dic[f"{study}_upper_plot"] = []
            dic[f"{study}_mid_plot"] = []
            dic[f"{study}_bottom_plot"] = []
            for nrst in range(len(dic[f"{study}_rst"].report_steps)):
                dic[f"{study}_upper_plot"].append(
                    dic[f"{study}_{quantity}_array"][nrst][dic[f"{study}_wellid"]]
                )
                dic[f"{study}_mid_plot"].append(
                    dic[f"{study}_{quantity}_array"][nrst][
                        dic[f"{study}_wellid"]
                        + dic[f"{study}_ny"]
                        * max(dic[f"{study}_nx"], dic[f"{study}_ny"])
                        * (round(0.5 * dic[f"{study}_nz"]) - 1)
                    ]
                )
                dic[f"{study}_bottom_plot"].append(
                    dic[f"{study}_{quantity}_array"][nrst][
                        dic[f"{study}_wellid"]
                        + dic[f"{study}_ny"]
                        * max(dic[f"{study}_nx"], dic[f"{study}_ny"])
                        * (dic[f"{study}_nz"] - 1)
                    ]
                )
            dic["axis"].plot(
                dic[f"{study}_report_time"],
                dic[f"{study}_upper_plot"],
                label=f"{dic['names'][0]} ({study})",
                color=dic["colors"][j],
                linestyle=dic["linestyle"][0],
            )
            dic["axis"].plot(
                dic[f"{study}_report_time"],
                dic[f"{study}_mid_plot"],
                label=f"{dic['names'][1]} ({study})",
                color=dic["colors"][j],
                linestyle=dic["linestyle"][1],
            )
            dic["axis"].plot(
                dic[f"{study}_report_time"],
                dic[f"{study}_bottom_plot"],
                label=f"{dic['names'][2]} ({study})",
                color=dic["colors"][j],
                linestyle=dic["linestyle"][2],
            )
        dic["axis"].set_ylabel(f"{dic['labels'][i]} {dic['units'][i]}")
        dic["axis"].set_xlabel("Time")
        dic["axis"].legend()
        dic["axis"].xaxis.set_tick_params(size=6, rotation=45)
        dic["fig"].savefig(
            f"{dic['where']}/nearwell_{quantity}.png", bbox_inches="tight"
        )

        plt.close()

    return dic


if __name__ == "__main__":
    main()
