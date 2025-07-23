# SPDX-FileCopyrightText: 2023-2025, NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

""""
Script to plot the capillary number
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt

def nca(r, m_r):
    return (M_U * m_r * L_C) / (RHOG * PHI * PERM * P_E * HEIGHT * 2 * 3.1416 * r)

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
COLORS = [
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

QRATE = [3,5,10,15,20,30]
NPRUNS = 6

HEIGHT = 100
PHI = 0.1
PERM = 101.3 / 1.01324997e15
RHOG = 636
M_U = 4.8e-5
P_E = 1.96e3
L_C = 1

fig, axis = plt.subplots()

for i, qrate in enumerate(QRATE):
    r = np.linspace(0.15, 20, 1000)
    n_ca = nca(r, QRATE[i])
    axis.plot(r, n_ca, lw=3, color=COLORS[i], label =f"M = {QRATE[i]} kg/s")
axis.set_xlabel(r"d [m]")
axis.set_ylabel(r"n$_{ca}$ [-]")
axis.set_yscale("log")
axis.legend()
fig.savefig(f"nca.png", bbox_inches="tight")