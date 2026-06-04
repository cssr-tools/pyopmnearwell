# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

"""Case 4 in the publication"""

import os
import subprocess
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

whr = Path(__file__).resolve().parent
cwd = os.getcwd()

GDENS = 1.86843
CONVF = 1.0e-9

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

folders = ["neglecting_salt_precipitation", "including_salt_precipitation"]

for folder in folders:
    subprocess.run(["python3", f"{whr}/{folder}/run_simulations.py"], check=True)

os.chdir(cwd)

colors = matplotlib.colormaps["tab20"]
markers = [
    "o",
    "v",
    "^",
    "<",
    ">",
    "D",
    "1",
    "2",
    "3",
    "4",
    "8",
    "s",
    "p",
    "*",
    "h",
    "H",
    "+",
    "x",
    "D",
    "d",
    "|",
    "_",
    "P",
    "X",
]

quantities = ["bhpxyear", "fgmit", "rmdt", "maxwbhp", "mindistance", "mass_salt"]
units = ["bar year", "Mt", "\\%", "bar", "m", "t"]
descriptions = [
    "BHP integretaed over time",
    r"Injected CO$_2$",
    r"Dissolved CO$_2$",
    "Max well BHP",
    r"CO$_2$ distance to the well",
    "Precipitated salt",
]

data_all = {}
names = None
schedules = None

for folder in folders:
    data_all[folder] = {}
    schedules = np.load(f"{whr}/{folder}/schedules.npy")
    names = np.load(f"{whr}/{folder}/names.npy")
    for quantity in quantities:
        data = np.load(f"{whr}/{folder}/{quantity}.npy")
        if quantity == "fgmit":
            data = data * GDENS * CONVF
        data_all[folder][quantity] = data

ordered = np.argsort(data_all[folders[0]]["bhpxyear"])

for j, (quantity, description) in enumerate(zip(quantities, descriptions)):
    fig, axis = plt.subplots()
    for i, folder in enumerate(folders):
        data = data_all[folder][quantity]
        axis.plot(
            range(len(schedules)),
            data[ordered],
            color=colors(4 + 2 * i),
            linestyle="",
            marker=markers[i],
            markersize=5,
            label=folder,
        )
    axis.set_xticks(np.round(np.linspace(0, len(schedules) - 1, len(schedules)), 2))
    axis.set_xticklabels([names[index] for index in ordered], rotation=270)
    ylabel = description + f" [{units[j]}]"
    axis.set_ylabel(f"{ylabel}")
    if quantity == "rmdt":
        axis.set_ylabel(r"Dissolved CO$_2$ [$\%$]")
    if quantity in ["fgmit", "rmdt"]:
        axis.set_ylim(0)
    axis.set_xlabel(r"Sequence in the schedule [-]")
    axis.legend(loc="best")

    xticklabels = axis.get_xticklabels()
    if len(xticklabels) > 0:
        xticklabels[0].set_color("blue")
        xticklabels[-1].set_color("blue")
        mid_index = len(xticklabels) // 2
        xticklabels[mid_index].set_color("blue")

    fig.savefig(f"{quantity}.png", bbox_inches="tight")
