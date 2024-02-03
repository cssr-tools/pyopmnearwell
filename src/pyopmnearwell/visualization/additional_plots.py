# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script for plotting
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def final_time_maps(dic):
    """
    Function to plot the 2D maps for the different reservoirs and quantities

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic["quantity"] += ["concentration"]
    dic["labels"] += ["Concentration"] + dic["rock"]
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
            if quantity == "pressure":
                axis.set_title(f"{dic['labels'][j]} [bar]")
            elif quantity == "concentration":
                axis.set_title(f"{dic['labels'][j]} " + r"[kg/m$^3$]")
            elif quantity == "permeability":
                axis.set_title(f"{dic['labels'][j]} [mD]")
            else:
                axis.set_title(f"{dic['labels'][j]} [-]")
            imag = axis.pcolormesh(
                dic[f"{study}_xcor"],
                dic[f"{study}_zcor"],
                dic[f"{study}_{quantity}_plot"],
                shading="flat",
                cmap=dic["cmaps"][j],
            )
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
                format=lambda x, _: f"{x:.1E}",
            )
            imag.set_clim(
                dic[f"{study}_{quantity}_plot"].min(),
                maxbar,
            )
            axis.grid()
            fig.savefig(f"{dic['where']}/{quantity}_2D.png", bbox_inches="tight")
            axis.set_xlim(right=dic["zoom"])
            fig.savefig(f"{dic['where']}/{quantity}_2D_zoom.png", bbox_inches="tight")
            plt.close()
    return dic


def saltprec_plots(dic):
    """
    Additional plots for sal precipittaion
    """
    nca_nb(dic)
    factors(dic)


def factors(dic):
    """
    Perfeability and J factor
    """
    study = dic["folders"][0]
    for i, (name, label, norm) in enumerate(
        zip(
            ["permfact", "pcfact"],
            [r"$k/k_0$", r"$\sqrt{(k_0\phi)/(\phi_0k)}$"],
            ["min", "max"],
        )
    ):
        table = dic["exe"] + "/" + study + f"/preprocessing/{name.upper()}.INC"
        if os.path.isfile(table):
            fig, axis = plt.subplots()
            poro, fact = [], []
            with open(table, "r", encoding="utf8") as file:
                for row in csv.reader(file, delimiter=" "):
                    if len(row) > 0:
                        if row[0] == "/":
                            break
                        if len(row) == 2:
                            poro.append(float(row[0]))
                            fact.append(float(row[1]))
            axis.plot(
                poro,
                fact,
                lw=2,
                color="m",
                label=f"{norm} = {min(fact) if i ==0 else max(fact):.6E}",
            )
            axis.set_xlabel(r"$\phi/\phi_0$")
            axis.set_ylabel(f"{label}")
            axis.legend()
            axis.set_xlim([0, 1])
            fig.savefig(f"{dic['where']}/{name}.png", bbox_inches="tight")


def nca_nb(dic):
    """
    Capillary and bond numbers
    """
    height = dic[f"{dic['folders'][0]}_zmz"][-1]
    d_z = height / (len(dic[f"{dic['folders'][0]}_zmz"]) - 1)
    phi = np.mean(dic[f"{dic['folders'][0]}_porosity_array"])
    perm = np.mean(dic[f"{dic['folders'][0]}_permeability_array"]) / 1.01324997e15
    rhog = np.mean(dic[f"{dic['folders'][0]}_denn_array"])
    rhol = np.mean(dic[f"{dic['folders'][0]}_denw_array"])
    m_u = np.mean(dic[f"{dic['folders'][0]}_viscn_array"]) * 1e-3
    p_e = dic["safu"][0][4] * 1e5
    m_r = (
        360
        * np.mean(dic[f"{dic['folders'][0]}_injection_raten"])
        * dic[f"{dic['folders'][0]}_rhon_ref"]
        / (dic["dims"][1] * 86400.0)
    )
    l_c = dic[f"{dic['folders'][0]}_xmx"][1]
    r_d = dic[f"{dic['folders'][0]}_xmx"][1]
    n_ca = (m_u * m_r * l_c) / (rhog * phi * perm * p_e * height * 2 * 3.1416 * r_d)
    n_b = (9.81 * (rhol - rhog) * d_z) / p_e
    with open(
        "nca_nb.csv",
        "w",
        encoding="utf8",
    ) as file:
        file.write(f"Nca = {n_ca:.6E} \n")
        file.write(f"Nb = {n_b:.6E} \n")


def over_time_saltprec(dic):
    """
    Function to plot the 1D normed quantities along the z direction

    Args:
        dic (dict): Global dictionary with required parameters

    """
    fig, axis = plt.subplots()
    for i, study in enumerate(dic["folders"]):
        axis.plot(
            dic[f"{study}_report_time"],
            dic[f"{study}_totalsaltprec"],
            label=f"{study}",
            color=dic["colors"][i],
        )
    axis.set_xlabel("Time")
    axis.set_ylabel("Total precipitated salt [kg]")
    axis.legend()
    axis.xaxis.set_tick_params(size=6, rotation=45)
    fig.savefig(f"{dic['where']}/cumulative_saltprec.png", bbox_inches="tight")
