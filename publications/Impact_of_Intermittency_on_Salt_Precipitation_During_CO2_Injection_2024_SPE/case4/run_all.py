# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import matplotlib.pyplot as plt
import numpy as np
import matplotlib
import os
import subprocess
import matplotlib

GDENS = 1.86843  # CO2 reference density
CONVF  = 1.0E-9 # kilograms to megatonnes

font = {"family": "normal", "weight": "normal", "size": 16}
matplotlib.rc("font", **font)
plt.rcParams.update(
    {
        "text.usetex": True,
        "font.family": "monospace",
        "legend.columnspacing": 0.9,
        "legend.handlelength": 1.5,
        "legend.fontsize": 12,
        "lines.linewidth": 4,
        "axes.titlesize": 16,
        "axes.grid": True,
        "figure.figsize": (10, 5),
    }
)

folders = sorted([name for name in os.listdir(".") if os.path.isdir(name)])
cwd = os.getcwd()
for folder in folders:
  os.chdir(f"{cwd}/{folder}")
  subprocess.run(
      ["python3", "run_simulations.py"], check=True
  )
os.chdir(f"{cwd}")
colors = matplotlib.colormaps["tab20"]
markers = ['o', 'v', '^', '<', '>', 'D', '1', '2', '3', '4', '8', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_', 'P', 'X']

quantities = ['bhpxyear', "fgit", "rmdt", 'maxwbhp', 'mindistance', "mass_salt"]
units = ["bar year", "Mt", "\\%", "bar", "m", "t"]
descriptions = ["BHP integretaed over time", r"Injected CO$_2$", r"Dissolved CO$_2$", "Max well BHP", r"CO$_2$ distance to the well", "Precipitated salt"]

for j,(quantity, description) in enumerate(zip(quantities,descriptions)): 
    fig, axis = plt.subplots()
    for i, folder in enumerate(folders):
        schedules = np.load(f'{folder}/schedules.npy')
        data = np.load(f'{folder}/{quantity}.npy')
        if quantity == "fgit":
            data *= GDENS * CONVF
        names = np.load(f'{folder}/names.npy')
        if i+j==0:
            ordered = np.argsort(data)
        axis.plot(
            range(len(schedules)),
            data[ordered],
            color=colors(4+2*i),
                linestyle="",
                marker=markers[i],
                markersize=5,
                label=folder,
        )
    axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, len(schedules)), 2))
    axis.set_xticklabels([names[i] for i in ordered], rotation=270)
    ylabel = description + f" [{units[j]}]"
    axis.set_ylabel(f"{ylabel}")
    if quantity == "rmdt":
        axis.set_ylabel(r"Dissolved CO$_2$ [$\%$]")
    if quantity in ["fgit", "rmdt"]:
        axis.set_ylim(0)
    axis.set_xlabel(r"Sequence in the schedule [-]")
    axis.legend(loc='best')
    plt.setp(axis.get_xticklabels()[0], color='blue')
    plt.setp(axis.get_xticklabels()[-1], color='blue')
    plt.setp(axis.get_xticklabels()[24], color='blue')
    fig.savefig(f"{quantity}.png",bbox_inches='tight')