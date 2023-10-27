# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-FileCopyrightText: 2023 UiB
# SPDX-License-Identifier: GPL-3.0
# pylint: skip-file
""""Run simulations with machine learned well models."""

from __future__ import annotations

import csv
import logging
import os
import pathlib
import shutil
from typing import Any, Literal, Optional

from mako import exceptions
from mako.template import Template

from pyopmnearwell.utils.mako import fill_template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dirname: pathlib.Path = pathlib.Path(__file__).parent


def recompile_flow(
    scalingsfile: pathlib.Path,
    opm_path: pathlib.Path,
    StandardWell_impl_template: Literal[
        "co2_3_inputs", "co2_5_inputs", "h2o_2_inputs", "co2_local_stencil"
    ],
    StandardWell_template: Literal["base", "local_stencil"] = "base",
    stencil_size: int = 3,
    local_feature_names: Optional[list[str]] = None,
) -> None:
    """Fill ``StandardWell_impl`` and recompile ``flow_gaswater_dissolution_diffuse``.

    Note: Once scaling layers are implemented directly into OPM, this might be
    deprecated. However, it might still be needed to deal with different stencils and
        features per cell.

    Args:
        scalingsfile (pathlib.Path): Path to the csv file containing the input and
            output scalings for the model.
        opm_path (pathlib.Path): Path to a OPM installation with ml functionality.
        StandardWell_impl_template (Literal["co2_3_inputs", "co2_5_inputs",
            "h2o_2_inputs", "co2_local_stencil"]): Template for
            ``StandardWell_impl.hpp``. Decides the neural network architecture.
        StandardWell_template (Literal["base", "local_stencil"], optional): Template for
        ``StandardWell.hpp``. Defaults to "base".
        stencil_size (int, optional): The size of the vertical stencil of the model.
            Defaults to 3.
        local_feature_names (Optional[list[str]], optional): List of local feature names
            that are input to the model. Defaults to Optional.

    Returns:
        None

    Raises:
        ValueError: If ``scalingsfile`` contains an invalid row.

    """
    # Ensure ``scalingsfile`` and ``opm_path`` are ``Path`` objects.
    scalingsfile = pathlib.Path(scalingsfile)
    opm_path = pathlib.Path(opm_path)

    if local_feature_names is None:
        local_feature_names = []

    opm_well_path: pathlib.Path = (
        opm_path / "opm-simulators" / "opm" / "simulators" / "wells"
    )
    template_path: pathlib.Path = dirname / ".." / "templates"

    # Get the scaling and write it to the C++ mako that integrates nn into OPM.
    feature_min: list[float] = []
    feature_max: list[float] = []
    feature_range: list[float] = [-1.0, 1.0]
    target_range: list[float] = [-1.0, 1.0]
    with scalingsfile.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=["variable", "min", "max"])

        # Skip the header
        next(reader)

        for row in reader:
            if row["variable"].startswith("output"):
                target_min: float = float(row["min"])
                target_max: float = float(row["max"])
            elif row["variable"].startswith("input"):
                feature_min.append(float(row["min"]))
                feature_max.append(float(row["max"]))
            elif row["variable"] == "feature_range":
                feature_range[0] = float(row["min"])
                feature_range[1] = float(row["max"])
            elif row["variable"] == "target_range":
                target_range[0] = float(row["min"])
                target_range[1] = float(row["max"])
            else:
                raise ValueError("Name of scaling variable is invalid.")

    var: dict[str, Any] = {
        "xmin": feature_min,
        "xmax": feature_max,
        "ymin": target_min,
        "ymax": target_max,
        "x_range_min": feature_range[0],
        "x_range_max": feature_range[1],
        "y_range_min": target_range[0],
        "y_range_max": target_range[1],
        "stencil_size": stencil_size,
        "cell_feature_names": local_feature_names,
    }
    filledtemplate: str = fill_template(
        var,
        filename=str(
            template_path / "standardwell_impl" / f"{StandardWell_impl_template}.mako"
        ),
    )
    with (opm_well_path / "StandardWell_impl.hpp").open("w", encoding="utf-8") as file:
        file.write(filledtemplate)

    shutil.copyfile(
        template_path / "standardwell" / f"{StandardWell_template}.hpp",
        opm_well_path / "StandardWell.hpp",
    )

    # Recompile flow.
    os.chdir(opm_path / "build" / "opm-simulators")
    os.system("make -j5 flow_gaswater_dissolution_diffuse")


def run_integration(
    runspecs: dict[str, Any], savepath: pathlib.Path, makofile: str | pathlib.Path
) -> None:
    """Runs ``pyopmnearwell`` simulations for the specified runspecs.

    Note: All "variables" need to

    Args:
        runspecs (dict[str, Any]): Contains at least two keys "variables" and
            "constants". The values of both keys are dictionaries and their union has to
            contain all parameters to fill the simulation template. Each key in the
            "variables"  dictionary is a list and this function loops through all lists
            in parallel and runs a simulation for each.
        savepath (str): Path to save the output files.
        makofile (str): Path to the ``pyopmnearwell`` deck template for the simulations.

    Returns:
        None

    """
    # Ensure ``savepath`` is a ``Path`` objects.
    savepath = pathlib.Path(savepath)

    variables: dict[str, list[float]] = runspecs["variables"]
    constants: dict[str, float] = runspecs["constants"]

    mytemplate: Template = Template(filename=str(makofile))
    if len({len(value) for value in variables.values()}) != 1:
        raise ValueError("All variables need to have the same number of values.")
    # Ignore MyPy complaining.

    # Loop through all variables in runspecs.
    for i in range(len(list(variables.values())[0])):  # type: ignore
        logger.info(f"Write pyopmnearwell deck for {i}th integration run")

        # Fill template for each run.
        constants.update(
            {variable: values[i] for variable, values in variables.items()}
        )
        try:
            filledtemplate = mytemplate.render(**constants)
        except Exception as error:
            print(exceptions.text_error_template().render())
            raise error
        with (savepath / f"run_{i}.txt").open("w", encoding="utf-8") as file:
            file.write(filledtemplate)

        # Use our pyopmnearwell friend to run the 3D simulations and compare the
        # results.
        logger.info(f"Run {i}th integration run")
        os.chdir(savepath)
        os.system(f"pyopmnearwell -i run_{i}.txt -o run_{i} -p off")
