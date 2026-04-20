# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-FileCopyrightText: 2023 UiB
# SPDX-License-Identifier: GPL-3.0
# pylint: skip-file
""" "Run simulations with machine learned well models.

Check the https://github.com/cssr-tools/ML_near_well/ repo for examples on how to use
the ``recompile_flow`` and ``run_integration`` functions.

``recompile_flow`` can only used for well models at the moment, however the
functionality could easily be extended to replace other parts of the OPM simulator
before recompiling.

"""

from __future__ import annotations

import csv
import logging
import pathlib
import shutil
import subprocess
from typing import Any, Optional

from mako import exceptions
from mako.template import Template

from pyopmnearwell.utils.mako import fill_template

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _find_opm_well_path(opm_path: pathlib.Path) -> pathlib.Path:
    """Find the OPM wells source directory for known source layouts."""
    candidates = [
        opm_path / "opm-simulators" / "opm" / "simulators" / "wells",
        opm_path / "opm" / "simulators" / "wells",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(
        f"Could not find OPM wells source directory under '{opm_path}'."
    )


def _find_opm_build_path(opm_path: pathlib.Path) -> pathlib.Path:
    """Find the OPM build directory for known build layouts."""
    candidates = [
        opm_path / "opm-simulators" / "build",
        opm_path / "build" / "opm-simulators",
        opm_path / "build",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(f"Could not find OPM build directory under '{opm_path}'.")


def _backup_default_standardwell_files(opm_well_path: pathlib.Path) -> None:
    """Store pristine StandardWell files once so they can be restored later."""
    default_header = opm_well_path / "StandardWell.default.hpp"
    default_impl = opm_well_path / "StandardWell_impl.default.hpp"
    header = opm_well_path / "StandardWell.hpp"
    impl = opm_well_path / "StandardWell_impl.hpp"

    if not default_header.exists():
        shutil.copyfile(header, default_header)
    if not default_impl.exists():
        shutil.copyfile(impl, default_impl)


def _restore_default_standardwell_files(opm_well_path: pathlib.Path) -> None:
    """Restore pristine StandardWell files previously saved by backup."""
    default_header = opm_well_path / "StandardWell.default.hpp"
    default_impl = opm_well_path / "StandardWell_impl.default.hpp"
    header = opm_well_path / "StandardWell.hpp"
    impl = opm_well_path / "StandardWell_impl.hpp"

    if not default_header.exists() or not default_impl.exists():
        raise FileNotFoundError(
            "Default StandardWell files were not found. Run recompile_flow once "
            "without reset to create backups first."
        )

    shutil.copyfile(default_header, header)
    shutil.copyfile(default_impl, impl)


def recompile_flow(
    scalingsfile: pathlib.Path,
    opm_path: pathlib.Path,
    StandardWell_impl_template: pathlib.Path | None = None,
    StandardWell_template: pathlib.Path | None = None,
    stencil_size: int = 3,
    local_feature_names: Optional[list[str]] = None,
    ml_model_path: Optional[pathlib.Path] = None,
    reset: bool = False,
) -> None:
    """Fill ``StandardWell_impl`` and recompile ``flow_gaswater_dissolution_diffuse``.

    Note: Once scaling layers are implemented directly into OPM, this might be
    deprecated. However, it might still be needed to deal with different stencils and
        features per cell.

    Args:
        scalingsfile (pathlib.Path): Path to the csv file containing the input and
            output scalings for the model.
        opm_path (pathlib.Path): Path to a OPM installation with ml functionality.
        StandardWell_impl_template (pathlib.Path): Template for
            ``StandardWell_impl.hpp``. Decides the neural network architecture.
        StandardWell_template (pathlib.Path): Template for ``StandardWell.hpp``.
        stencil_size (int, optional): The size of the vertical stencil of the model.
            Defaults to 3.
        local_feature_names (Optional[list[str]], optional): List of local feature names
            that are input to the model. Defaults to Optional.

    Returns:
        None

    Raises:
        ValueError: If ``scalingsfile`` contains an invalid row.

    """
    if (
        StandardWell_impl_template is None
        or StandardWell_template is None
        or ml_model_path is None
    ) and not reset:
        raise ValueError(
            "Please provide templates for StandardWell_impl and StandardWell and a"
            " ml_model_path, or set reset to True."
        )

    # Ensure ``scalingsfile`` and ``opm_path`` are ``Path`` objects.
    scalingsfile = pathlib.Path(scalingsfile)
    opm_path = pathlib.Path(opm_path)

    if local_feature_names is None:
        local_feature_names = []

    opm_well_path = _find_opm_well_path(opm_path)
    opm_build_path = _find_opm_build_path(opm_path)

    # Save defaults once and support restoring them for cleanup runs.
    _backup_default_standardwell_files(opm_well_path)
    if reset:
        _restore_default_standardwell_files(opm_well_path)
        subprocess.run(
            ["make", "-j5", "flow_gaswater_dissolution_diffuse"],
            cwd=opm_build_path,
            check=True,
        )
        return None

    opm_well_path: pathlib.Path = (
        opm_path / "opm-simulators" / "opm" / "simulators" / "wells"
    )

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
        "ml_model_path": ml_model_path,
    }

    # Fill templates and copy into OPM installation.
    filledtemplate: str = fill_template(var, filename=str(StandardWell_impl_template))
    with (opm_well_path / "StandardWell_impl.hpp").open("w", encoding="utf-8") as file:
        file.write(filledtemplate)

    shutil.copyfile(StandardWell_template, opm_well_path / "StandardWell.hpp")

    # Recompile flow.
    subprocess.run(
        ["make", "-j5", "flow_gaswater_dissolution_diffuse"],
        cwd=opm_build_path,
        check=True,
    )


def run_integration(
    runspecs: dict[str, Any], savepath: pathlib.Path, makofile: str | pathlib.Path
) -> None:
    """Runs ``pyopmnearwell`` simulations for the specified runspecs.

    Note: All "variables" in runspecs need to have the same number of values.

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
            # We assume that filledtemplate is a string and ignore Pylance complaining.
            file.write(filledtemplate)  # type: ignore

        # Use our pyopmnearwell friend to run the 3D simulations and compare the
        # results.
        logger.info(f"Run {i}th integration run")
        subprocess.run(
            ["pyopmnearwell", "-i", f"run_{i}.txt", "-o", f"run_{i}", "-p", "off"],
            cwd=savepath,
            check=True,
        )
