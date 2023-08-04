# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-FileCopyrightText: 2023 UiB
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow for a random input variable
"""

import os
import math
import numpy as np
from ecl.eclfile import EclFile
from mako.template import Template
import matplotlib
import matplotlib.pyplot as plt

np.random.seed(7)


def compute_peaceman(h_cell: float, k: float, r_e: float, r_w: float) -> float:
    r"""Compute the well productivity index (adjusted for density and viscosity)
    from the Peaceman well model.
    .. math::
        WI\cdot\frac{\mu}{\rho} = \frac{2\pi hk}{\ln (r_e/r_w)}
    Parameters:
        h_cell: Thickness of the well block.
        k: Permeability.
        r_e: Equivalent well-block radius.
        r_w: Wellbore radius.
    Returns:
        :math:`WI\cdot\frac{\mu}{\rho}`
    """
    w_i = (2 * math.pi * h_cell * k) / (math.log(r_e / r_w))
    return w_i


# Give the full path to FLOW
FLOW = "/Users/dmar/Github/pyopmnearwell/build/opm-simulators/bin/flow_gaswater_dissolution_diffuse"
PWD = os.getcwd()

# Write the configuration files
var = {"flow": FLOW, "pwd": PWD}
for name in ["nearwell", "3d_flow_wellmodel", "3d_ml_wellmodel"]:
    mytemplate = Template(filename=f"h2o_{name}.mako")
    filledtemplate = mytemplate.render(**var)
    with open(
        f"h2o_{name}.txt",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)

# Run the near-well simulations
os.system("pyopmnearwell -i h2o_nearwell.txt -o h2o_nearwell")

# Read and Set the values (in SI)
POSITIONS = np.load("./h2o_nearwell/output/xspace.npy")
DISTANCE = 0.5 * (POSITIONS[2:] + POSITIONS[1:-1])
THICKNESS = 1
PERMEABILITY = 1013.25 * 9.869233e-16
WELLRADI = 0.05
RATE = 6 * 1.001896e01 / 86400
BOFAC = 1.0
VISCOSCITY = 0.6532 * 0.001

# Compute the well index (simulated and from the analytical solution)
wi = []
wi2 = []
for r in DISTANCE:
    wi2.append(
        compute_peaceman(THICKNESS, PERMEABILITY, r, WELLRADI) * BOFAC / VISCOSCITY
    )
rst = EclFile("./h2o_nearwell/output/RESERVOIR.UNRST")
pressure = np.array(rst.iget_kw("PRESSURE")[-1])
pw = pressure[0]
wi = RATE / ((pw - pressure[1:]) * 1e5)

# Plot both WI
fig, axis = plt.subplots()
axis.set_yscale("log")
axis.plot(
    DISTANCE,
    wi,
    color=matplotlib.colormaps["tab20"].colors[0],
    linestyle="",
    marker="*",
    markersize=5,
    label="sim",
)
axis.plot(
    DISTANCE,
    wi2,
    color=matplotlib.colormaps["tab20"].colors[1],
    linestyle="",
    marker=".",
    markersize=5,
    label="peaceman",
)
axis.set_ylabel(r"WI [sm{^3}/(Pa s)]", fontsize=12)
axis.set_xlabel("Distance to well [m]", fontsize=12)
axis.legend(fontsize=6)
fig.savefig("analytical_and_simulated_wellindex.png")

# Save the required quantities for the ML routine
np.save("re", DISTANCE)
np.save("wi", wi)

# Run the ML script
os.system("python3 ml_routine.py")

# Use our pyopmnearwell friend to run the 3D simulations and compare the results
os.system("rm -rf h2o_nearwell")
os.system("pyopmnearwell -i h2o_3d_flow_wellmodel.txt -o h2o_3d_flow_wellmodel")
os.system("pyopmnearwell -i h2o_3d_ml_wellmodel.txt -o h2o_3d_ml_wellmodel")
os.system("pyopmnearwell -c compare")
