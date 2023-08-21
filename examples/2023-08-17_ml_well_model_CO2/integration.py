# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-FileCopyrightText: 2023 UiB
# SPDX-License-Identifier: GPL-3.0
""""Run a CO2 injection in flow both with the Peaceman well model and machine learned
well model."""

from __future__ import annotations

import csv
import os
import shutil
from typing import Any

import runspecs
from mako.template import Template

import pyopmnearwell.utils.units as units

# Path to the simulation *.makos.
PATH: str = os.path.dirname(os.path.realpath(__file__))

# Path to OPM with ml and flow.
OPM_ML: str = "/home/peter/Documents/2023_CEMRACS/opm_ml"
FLOW: str = f"{OPM_ML}/build/opm-simulators/bin/flow_gaswater_dissolution_diffuse"

# Get the scaling and write it to the C++ mako that integrates nn into OPM.
# feature_min: list[float] = []
# feature_max: list[float] = []
# with open(os.path.join(PATH, "model_pressure_radius_WI", "scales.csv")) as csvfile:
#     reader = csv.DictReader(csvfile, fieldnames=["variable", "min", "max"])
#     for row in reader:
#         match row["variable"]:
#             case "pressure":
#                 feature_min.append(float(row["min"]))
#                 feature_max.append(float(row["max"]))
#             case "time":
#                 feature_min.append(float(row["min"]))
#                 feature_max.append(float(row["max"]))
#             case "radius":
#                 feature_min.append(float(row["min"]))
#                 feature_max.append(float(row["max"]))
#             case "WI":
#                 target_min: float = float(row["min"])
#                 target_max: float = float(row["max"])

# var: dict[str, Any] = {
#     "xmin": feature_min,
#     "xmax": feature_max,
#     "ymin": target_min,
#     "ymax": target_max,
# }
# mytemplate = Template(filename=os.path.join(PATH, "StandardWell_impl.mako"))
# filledtemplate = mytemplate.render(**var)
# with open(
#     f"{OPM_ML}/opm-simulators/opm/simulators/wells/StandardWell_impl.hpp",
#     "w",
#     encoding="utf8",
# ) as file:
#     file.write(filledtemplate)

# shutil.copyfile(
#     os.path.join(PATH, "StandardWell.hpp"),
#     f"{OPM_ML}/opm-simulators/opm/simulators/wells/StandardWell.hpp",
# )

# # Recompile flow.
# os.chdir(f"{OPM_ML}/build/opm-simulators")
# os.system("make -j5 flow_gaswater_dissolution_diffuse")


INIT_PRESSURE: float = (
    0.5
    * (runspecs.INIT_PRESSURE_MIN + runspecs.INIT_PRESSURE_MAX)
    * units.BAR_TO_PASCAL
)  # unit: [Pa];
INIT_PRESSURE: float = 51 * units.BAR_TO_PASCAL
# NOTE: During training we train on the wellblock pressure, not on the pressure of the
# entire reservoir.

# Write the configuration files for the comparison in the 3D reservoir
var = {
    "flow": FLOW,
    "perm": runspecs.PERMEABILITY * units.MILIDARCY_TO_M2,
    "pressure": INIT_PRESSURE,
    "temperature": runspecs.TEMPERATURE,
    "radius": runspecs.WELL_RADIUS,
    "reservoir_size": runspecs.RESERVOIR_SIZE,
    "rate": runspecs.INJECTION_RATE,
    "pwd": PATH,
}

# Use our pyopmnearwell friend to run the 3D simulations and compare the results
os.chdir(os.path.join(PATH, "tests"))
for name in [
    # "3d_flow_wellmodel",
    # "3d_ml_wellmodel",
    # "3d_finescale_wellmodel_low",
    # "3d_finescale_wellmodel_middle",
    "3d_finescale_wellmodel_high",
]:
    mytemplate = Template(filename=f"co2_{name}.mako")
    filledtemplate = mytemplate.render(**var)
    with open(
        os.path.join(f"co2_{name}.txt"),
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    os.system(f"pyopmnearwell -i co2_{name}.txt -o co2_{name}")

# os.system("pyopmnearwell -c compare")
