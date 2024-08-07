# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-FileCopyrightText: 2023 UiB
# SPDX-License-Identifier: GPL-3.0
""""Run a CO2 injection in flow both with the Peaceman well model and machine learned
well model."""

import csv
import math
import os
from typing import Any

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from resdata.resfile import ResdataFile
from mako.template import Template

# Path to the simulation *.makos.
PATH: str = os.path.dirname(os.path.realpath(__file__))

# Path to OPM with ml and flow.
OPM_ML: str = "/home/peter/Documents/2023_CEMRACS/opm_ml"
FLOW: str = f"{OPM_ML}/build/opm-simulators/bin/flow_gaswater_dissolution_diffuse"

# Get the scaling and write it to the C++ mako that integrates nn into OPM.
feature_min: list[float] = []
feature_max: list[float] = []
with open(os.path.join(PATH, "model_pressure_radius_WI", "scales.csv")) as csvfile:
    reader = csv.DictReader(csvfile, fieldnames=["variable", "min", "max"])
    for row in reader:
        if row["variable"] == "init_pressure":
            feature_min.append(float(row["min"]))
            feature_max.append(float(row["max"]))
        elif row["variable"] == "radius":
            feature_min.append(float(row["min"]))
            feature_max.append(float(row["max"]))
        elif row["variable"] == "WI":
            target_min: float = float(row["min"])
            target_max: float = float(row["max"])

var: dict[str, Any] = {
    "xmin": feature_min,
    "xmax": feature_max,
    "ymin": target_min,
    "ymax": target_max,
}
mytemplate = Template(filename=os.path.join(PATH, "StandardWell_impl.mako"))
filledtemplate = mytemplate.render(**var)
with open(
    f"{OPM_ML}/opm-simulators/opm/simulators/wells/StandardWell_impl.hpp",
    "w",
    encoding="utf8",
) as file:
    file.write(filledtemplate)

# Recompile flow.
os.chdir(f"{OPM_ML}/build/opm-simulators")
os.system("make -j5 flow_gaswater_dissolution_diffuse")


PERMEABILITY: float = 1e-12  # unit: [m^2] Fixed during training.
INIT_PRESSURE: float = 7.2e6  # unit: [Pa]; slightly below critical point
# NOTE: During training we train on the wellblock pressure, not on the pressure of the
# entire reservoir.
TEMPERATURE: float = 30.9780  # unit: [C]; critical point; Fixed during training.
X: float = 2.500000e-01  # Outer coordinates of first cell.
Y: float = -1.443376e-01
WELLRADIUS: float = math.sqrt(X**2 + Y**2)  # unit: [m]; Fixed during training.
INJECTION_RATE: float = 5.352087e3  # unit: [kg/d]; Fixed during training.

# Write the configuration files for the comparison in the 3D reservoir
var = {
    "flow": FLOW,
    "perm": PERMEABILITY,
    "pressure": INIT_PRESSURE,
    "temperature": TEMPERATURE,
    "radius": WELLRADIUS,
    "rate": INJECTION_RATE,
    "pwd": PATH,
}

# Use our pyopmnearwell friend to run the 3D simulations and compare the results
os.chdir(PATH)
for name in [
    "3d_flow_wellmodel",
    "3d_ml_wellmodel",
    "3d_finescale_wellmodel",
    "3d_flow_wellmodel_large_reservoir",
    "3d_ml_wellmodel_large_reservoir",
    "3d_finescale_wellmodel_large_reservoir",
]:
    mytemplate = Template(filename=os.path.join(f"co2_{name}.mako"))
    filledtemplate = mytemplate.render(**var)
    with open(
        os.path.join(f"co2_{name}.txt"),
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(f"pyopmnearwell -i co2_{name}.txt -o co2_{name}")

# os.system("pyopmnearwell -c compare")
