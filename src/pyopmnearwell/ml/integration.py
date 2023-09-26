# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-FileCopyrightText: 2023 UiB
# SPDX-License-Identifier: GPL-3.0
""""Run a CO2 injection on reservoir-scale in flow with the Peaceman well model, machine
learned well model and a finescale simulation."""

from __future__ import annotations

import csv
import os
import shutil
from typing import Any

from mako.template import Template

dir: str = os.path.dirname(__file__)


def recompile_flow(scalesfile: str, opm_path: str) -> None:
    opm_well_path: str = os.path.join(
        opm_path, "opm-simulators", "opm", "simulators", "wells"
    )
    well_template_path: str = os.path.join(dir, "..", "templates", "standardwell_opm")
    # Get the scaling and write it to the C++ mako that integrates nn into OPM.
    feature_min: list[float] = []
    feature_max: list[float] = []
    with open(scalesfile) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=["variable", "min", "max"])
        for row in reader:
            if row["variable"] == "WI":
                target_min: float = float(row["min"])
                target_max: float = float(row["max"])
            else:
                feature_min.append(float(row["min"]))
                feature_max.append(float(row["max"]))
        var: dict[str, Any] = {
            "xmin": feature_min,
            "xmax": feature_max,
            "ymin": target_min,
            "ymax": target_max,
        }
        mytemplate = Template(
            filename=os.path.join(well_template_path, "WI.model"),
        )
        filledtemplate = mytemplate.render(**var)
        with open(
            os.path.join(opm_well_path, "StandardWell_impl.hpp"),
            "w",
            encoding="utf8",
        ) as file:
            file.write(filledtemplate)

    shutil.copyfile(
        os.path.join(well_template_path, "StandardWell.hpp"),
        os.path.join(opm_well_path, "StandardWell.hpp"),
    )

    # Recompile flow.
    os.chdir(os.path.join(opm_path, "build", "opm-simulators"))
    os.system("make -j5 flow_gaswater_dissolution_diffuse")


def run_integration(runspecs: dict[str, Any], savepath: str, makofile: str) -> None:
    variables: dict[str, list[float]] = runspecs["variables"]
    constants: dict[str, float] = runspecs["constants"]
    mytemplate = Template(filename=makofile)
    if len(set([len(value) for value in variables.values()])) != 1:
        raise ValueError("All variables need to have the same number of values.")
    # Ignore MyPy complaining.
    for i in range(len(list[variables.values()][0])):  # type: ignore
        # Fill template for each run.
        constants.update(
            {variable: values[i] for variable, values in variables.items()}
        )
        filledtemplate = mytemplate.render(**constants)
        with open(
            os.path.join(savepath, f"run_{i}.txt"),
            "w",
            encoding="utf8",
        ) as file:
            file.write(filledtemplate)

        # Use our pyopmnearwell friend to run the 3D simulations and compare the results.
        os.system(f"pyopmnearwell -i run_{i}.txt -o {savepath}")
