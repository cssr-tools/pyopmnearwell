# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script for plotting
"""

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
            # if quantity == "permfact":
            #    cmap = "jet_r"
            # else:
            #    cmap = "jet"
            imag = axis.pcolormesh(
                dic[f"{study}_xcor"],
                dic[f"{study}_zcor"],
                dic[f"{study}_{quantity}_plot"],
                shading="flat",
                cmap="jet",
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
                format=lambda x, _: f"{x:.2E}",
            )
            imag.set_clim(
                dic[f"{study}_{quantity}_plot"].min(),
                maxbar,
            )
            axis.grid()
            fig.savefig(f"{dic['where']}/{quantity}_2D.png", bbox_inches="tight")
            axis.set_xlim(right=20)
            fig.savefig(f"{dic['where']}/{quantity}_2D_zoom.png", bbox_inches="tight")
            plt.close()

    return dic
