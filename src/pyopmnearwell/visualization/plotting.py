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
from mpl_toolkits.axes_grid1 import make_axes_locatable
from pyopmnearwell.visualization.reading import read_simulations


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
    cmdargs = vars(parser.parse_known_args()[0])
    dic = {"folders": [cmdargs["folder"].strip()]}
    dic["plot"] = cmdargs["plot"].strip()  # Using ecl or opm
    dic["compare"] = cmdargs["compare"]  # Name of the compare plot
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
    dic["units"] = ["[bar]", "[-]"]
    dic["labels"] = ["Pressure", "Non-wetting saturation"]
    dic["linestyle"] = [
        (0, ()),
        (0, (1, 1)),
        "--",
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
        (0.12156862745098039, 0.4666666666666667, 0.7058823529411765),
        (1.0, 0.4980392156862745, 0.054901960784313725),
        (0.17254901960784313, 0.6274509803921569, 0.17254901960784313),
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
    dic = over_time_layers(dic)
    final_time_projections(dic)
    if dic["compare"]:
        return
    final_time_maps(dic)


def capillary_pressure(dic):
    """
    Function to plot the capillary pressure function

    Args:
        dic (dict): Global dictionary with required parameters

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
                    axis.set_xlabel("Non-wetting saturation", fontsize=12)
                else:
                    kind = 1
                    col = 2
                    axis.set_xlabel("Wetting saturation", fontsize=12)
                break
        data = read_table(table, kind)
        for j in range(len(data) - 1):
            axis.plot(
                [float(row[0]) for row in data[j]],
                [1e5 * float(row[col]) for row in data[j]],
                label=f"{study}_satnum_{j}",
                color=matplotlib.colormaps["tab20"].colors[2 * i],
                linestyle=dic["linestyle"][j],
                linewidth=2,
            )
    xvalue = np.array([float(row[0]) for row in data[0]])
    yvalue = np.array([float(row[col]) for row in data[0]])
    dic["cp_func"] = interp1d(xvalue, yvalue, fill_value="extrapolate")
    if yvalue[0] > 0:
        axis.set_yscale("log")
    axis.set_ylabel("Capillary Pressure [Pa]", fontsize=12)
    axis.set_xlim([0, 1])
    axis.legend(fontsize=10)
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


def final_time_maps(dic):
    """
    Function to plot the 2D maps for the different reservoirs and quantitiesdic[f'{study}_wellid']

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["quantity"] += ["concentration"]
    dic["labels"] += ["concentration"] + dic["rock"]
    for study in dic["folders"]:
        dic[f"{study}_xcor"], dic[f"{study}_zcor"] = np.meshgrid(
            dic[f"{study}_xmx"], dic[f"{study}_zmz"][::-1]
        )
        for j, quantity in enumerate(dic["quantity"] + dic["rock"]):
            dic[f"{study}_{quantity}_plot"] = np.zeros(
                [len(dic[f"{study}_zmz"]) - 1, len(dic[f"{study}_xmx"]) - 1]
            )
            for i in np.arange(0, len(dic[f"{study}_zmz"]) - 1):
                dic[f"{study}_{quantity}_plot"][-1 - i, :] = dic[
                    f"{study}_{quantity}_array"
                ][-1][
                    dic[f"{study}_wellid"]
                    + i
                    * max(dic[f"{study}_nx"], dic[f"{study}_ny"])
                    * dic[f"{study}_ny"] : i
                    * max(dic[f"{study}_nx"], dic[f"{study}_ny"])
                    * dic[f"{study}_ny"]
                    + dic[f"{study}_nx"]
                    + dic[f"{study}_wellid"]
                ]
            fig, axis = plt.subplots()
            imag = axis.pcolormesh(
                dic[f"{study}_xcor"],
                dic[f"{study}_zcor"],
                dic[f"{study}_{quantity}_plot"],
                shading="flat",
                cmap="jet",
            )
            if quantity == "pressure":
                axis.set_title(f"{dic['labels'][j]} [bar]")
            elif quantity == "concentration":
                axis.set_title(f"{dic['labels'][j]} " + r"[kg/m$^3$]")
            elif quantity == "permeability":
                axis.set_title(f"{dic['labels'][j]} [mD]")
            else:
                axis.set_title(f"{dic['labels'][j]} [-]")
            if quantity == "saturation":
                maxbar = 1.0
            else:
                maxbar = dic[f"{study}_{quantity}_plot"].max()
            axis.invert_yaxis()
            axis.set_xlabel("x [m]")
            axis.set_ylabel("z [m]")
            divider = make_axes_locatable(axis)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            vect = np.linspace(
                dic[f"{study}_{quantity}_plot"].min(),
                maxbar,
                4,
                endpoint=True,
            )
            fig.colorbar(
                imag,
                cax=cax,
                orientation="vertical",
                ticks=vect,
                format=lambda x, _: f"{x:.2E}",
            )
            imag.set_clim(
                dic[f"{study}_{quantity}_plot"].min(),
                maxbar,
            )
            fig.savefig(f"{dic['where']}/{quantity}_2D.png", bbox_inches="tight")
            plt.close()

    return dic


def final_time_projections(dic):
    """
    Function to plot the 1D projected quantities along the z direction

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["projection"] = [
        "top_cells",
        "middle_cells",
        "bottom_cells",
        "max",
        "min",
        "mean",
    ]
    for j, quantity in enumerate(dic["quantity"]):
        fig, axis = plt.subplots()
        for study in dic["folders"]:
            if dic[f"{study}_nz"] > 1:
                nlines = 3
                dic["names"] = ["Upper layer", "Mid layer", "Bottom layer"]
            else:
                nlines = 1
                dic["names"] = ["Simulation"]
            for projection in dic["projection"]:
                dic[f"{study}_{quantity}_{projection}"] = []
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
            if dic[f"{study}_wellid"] == 0:
                for k, projection in enumerate(dic["projection"][:nlines]):
                    axis.plot(
                        dic[f"{study}_xmidpoints"],
                        dic[f"{study}_{quantity}_{projection}"],
                        label=f"{dic['names'][k]} ({study})",
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
                    file.write(f"pw = {dic[f'{study}_well_pressure'][-1]:.6E} [bar]\n")
                    file.write(
                        f"p0 = {dic[f'{study}_pressure_array'][-1][dic[f'{study}_wellid']]:.6E}"
                        + " [bar]\n"
                    )
                    file.write(f"WI = {dic[f'{study}_WI']:.6E} [kg/(Bar day)]\n")
                    file.write(f"T = {dic[f'{study}_T']:.6E} [mD m]\n")
                    file.write("Distance [m] Pressure [bar]\n")
                    for distance, pressure in zip(
                        dic[f"{study}_xmidpoints"][:-1],
                        dic[f"{study}_pressure_{projection}"][:-1],
                    ):
                        file.write(f"{distance:.3E} {pressure:.3E}\n")
                    file.write(
                        f"{dic[f'{study}_xmidpoints'][-1]:.3E} "
                        + f"{dic[f'{study}_pressure_{projection}'][-1]:.3E}"
                    )
        axis.set_xlabel("Distance from wellbore [m]")
        axis.set_ylabel(f"{dic['labels'][j]} {dic['units'][j]}")
        axis.legend(fontsize=8)
        fig.savefig(f"{dic['where']}/{quantity}_1D.png", bbox_inches="tight")
        axis.set_xlim([-0.3, 20])
        fig.savefig(f"{dic['where']}/{quantity}_1D_zoom.png", bbox_inches="tight")
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
    for study in dic["folders"]:
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
            label=f"{study}",
        )
    dic["axis"][-1].set_title(
        f'Maximum horizontal distance to the well (sat thr={dic["sat_thr"]})'
    )
    dic["axis"][-1].set_ylabel("Distance [m]", fontsize=12)
    dic["axis"][-1].set_xlabel("Time [y]", fontsize=12)
    dic["axis"][-1].legend(fontsize=8)
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

    quantites = ["injectivity", "ratew", "raten", "pressure"]
    units = [
        "Injectivity [kg/(bar day)]",
        "Rate [kg/day]",
        "Rate [kg/day]",
        "Pressure [bar]",
    ]
    for i, quantity in enumerate(quantites):
        dic["fig"], dic["axis"] = plt.subplots()
        for study in dic["folders"]:
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
            for j, nrst in enumerate(dic[f"{study}_smsp_rst"][1:]):
                ratew = dic[f"{study}_injection_ratew"][nrst] * dic[f"{study}_rhow_ref"]
                raten = dic[f"{study}_injection_raten"][nrst] * dic[f"{study}_rhon_ref"]
                well_pressure = dic[f"{study}_well_pressure"][nrst]
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
                )
                dic["axis"].plot(
                    dic[f"{study}_rst_seconds"],
                    [
                        value[dic[f"{study}_wellid"]] - dic["cp_func"](1)
                        for value in dic[f"{study}_pressure_array"]
                    ],
                    label=f"cell ({study})",
                )
            else:
                dic["axis"].plot(
                    dic[f"{study}_rst_seconds"][1:],
                    dic[f"{study}_{quantity}_plot"],
                    label=f"{study}",
                )
        dic["axis"].set_ylabel(units[i], fontsize=12)
        dic["axis"].set_xlabel("Time [s]", fontsize=12)
        dic["axis"].legend(fontsize=8)
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
                dic[f"{study}_rst_seconds"],
                dic[f"{study}_upper_plot"],
                label=f"{dic['names'][0]} ({study})",
                color=dic["colors"][0],
                linestyle=dic["linestyle"][j],
            )
            dic["axis"].plot(
                dic[f"{study}_rst_seconds"],
                dic[f"{study}_mid_plot"],
                label=f"{dic['names'][1]} ({study})",
                color=dic["colors"][1],
                linestyle=dic["linestyle"][j],
            )
            dic["axis"].plot(
                dic[f"{study}_rst_seconds"],
                dic[f"{study}_bottom_plot"],
                label=f"{dic['names'][2]} ({study})",
                color=dic["colors"][2],
                linestyle=dic["linestyle"][j],
            )
        dic["axis"].set_ylabel(f"{dic['labels'][i]} {dic['units'][i]}", fontsize=12)
        dic["axis"].set_xlabel("Time [s]", fontsize=12)
        dic["axis"].legend(fontsize=8)
        dic["axis"].xaxis.set_tick_params(size=6, rotation=45)
        dic["fig"].savefig(
            f"{dic['where']}/nearwell_{quantity}.png", bbox_inches="tight"
        )

        plt.close()

    return dic


if __name__ == "__main__":
    main()
