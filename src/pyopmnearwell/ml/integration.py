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

import logging
import pathlib
import shutil
import subprocess
from typing import Any

from mako import exceptions
from mako.template import Template

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


def _find_opm_flow_path(opm_path: pathlib.Path) -> pathlib.Path:
    """Find the OPM flow source directory for known source layouts."""
    candidates = [
        opm_path / "opm-simulators" / "opm" / "simulators" / "flow",
        opm_path / "opm" / "simulators" / "flow",
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(
        f"Could not find OPM flow source directory under '{opm_path}'."
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


def _backup_default_standardwell_files(
    opm_path: pathlib.Path,
    opm_well_path: pathlib.Path,
    opm_flow_path: pathlib.Path,
) -> None:
    """Store pristine files once so they can be restored later."""
    files_to_backup = [
        opm_well_path / "StandardWell.hpp",
        opm_well_path / "StandardWell_impl.hpp",
        opm_well_path / "MLNearWellConfig.hpp",
        opm_well_path / "MLNearWellConfig.cpp",
        opm_flow_path / "FlowProblemParameters.cpp",
        opm_flow_path / "FlowProblemParameters.hpp",
        opm_path / "CMakeLists_files.cmake",
    ]

    for source_file in files_to_backup:
        default_file = pathlib.Path(source_file.stem + ".default" + source_file.suffix)
        if source_file.exists() and not default_file.exists():
            shutil.copyfile(source_file, default_file)


def _restore_default_standardwell_files(
    opm_path: pathlib.Path,
    opm_well_path: pathlib.Path,
    opm_flow_path: pathlib.Path,
) -> None:
    """Restore pristine files previously saved by backup."""
    files_to_restore = [
        opm_well_path / "StandardWell.hpp",
        opm_well_path / "StandardWell_impl.hpp",
        opm_flow_path / "FlowProblemParameters.cpp",
        opm_flow_path / "FlowProblemParameters.hpp",
        opm_path / "CMakeLists_files.cmake",
    ]

    missing_backups: list[pathlib.Path] = []
    for target_file in files_to_restore:
        default_file = pathlib.Path(target_file.stem + ".default" + target_file.suffix)
        if default_file.exists():
            shutil.copyfile(default_file, target_file)
        elif target_file.exists():
            # Remove files that were introduced by ML patching and had no default.
            target_file.unlink()
        else:
            missing_backups.append(default_file)

    if missing_backups:
        missing = ", ".join(str(path) for path in missing_backups)
        raise FileNotFoundError(
            "Default files were not found. Run recompile_flow once without reset "
            f"to create backups first. Missing backup files: {missing}"
        )


def recompile_flow(
    opm_path: pathlib.Path,
    new_files_path: pathlib.Path | None = None,
    reset: bool = False,
) -> None:
    """Copy updated and recompile ``flow_gaswater_dissolution_diffuse``.


    Args:
        opm_path (pathlib.Path): Path to a OPM installation with ml functionality.
        new_files_path (pathlib.Path | None): Path to a directory containing updated
            OPM files.
        reset (bool): If True, restore default OPM files and recompile.

    Returns:
        None

    Raises:
        ValueError: If ``replacement_dir_path`` is not provided when ``reset`` is False.
        FileNotFoundError: If the expected OPM file source directory or build directory
            cannot be found, or if the replacement files do not exist.

    """
    if (new_files_path is None) and not reset:
        raise ValueError(
            "Please provide a well files directory path or set reset to True."
        )

    # Ensure ``opm_path`` and ``well_files_path`` are ``Path`` objects.
    opm_path = pathlib.Path(opm_path)
    if new_files_path is not None:
        new_files_path = pathlib.Path(new_files_path)

    opm_well_path = _find_opm_well_path(opm_path)
    opm_build_path = _find_opm_build_path(opm_path)
    opm_flow_path = _find_opm_flow_path(opm_path)

    # Copy the new files or the default files to the OPM wells source directory
    # depending on the value of reset.

    if reset:
        _restore_default_standardwell_files(
            opm_path,
            opm_well_path,
            opm_flow_path,
        )

    else:
        _backup_default_standardwell_files(
            opm_path,
            opm_well_path,
            opm_flow_path,
        )
        for filename in [
            "StandardWell.hpp",
            "StandardWell_impl.hpp",
            "MLNearWellConfig.hpp",
            "MLNearWellConfig.cpp",
        ]:
            # Ignore MyPy. well_files_path is checked to be not None above.
            source_file = new_files_path / filename  # type: ignore
            if not source_file.exists():
                raise FileNotFoundError(
                    f"Replacement file '{source_file}' does not exist."
                )
            shutil.copyfile(source_file, opm_well_path / filename)  # type: ignore

        for filename in ["FlowProblemParameters.cpp", "FlowProblemParameters.hpp"]:
            # Ignore MyPy. well_files_path is checked to be not None above.
            source_file = new_files_path / filename  # type: ignore
            if not source_file.exists():
                raise FileNotFoundError(
                    f"Replacement file '{source_file}' does not exist."
                )
            shutil.copyfile(source_file, opm_flow_path / filename)  # type: ignore

        source_file = new_files_path / "CMakeLists_files.cmake"  # type: ignore
        if not source_file.exists():
            raise FileNotFoundError(f"Replacement file '{source_file}' does not exist.")
        shutil.copyfile(source_file, opm_path / "CMakeLists_files.cmake")  # type: ignore

    logger.info(
        f"Copied files to {opm_path}. Recompiling flow_gaswater_dissolution_diffuse..."
    )

    # Recompile flow with the copied files.
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
