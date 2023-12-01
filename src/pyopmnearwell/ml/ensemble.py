# pylint: skip-file
""""Run high-fidelity nearwell simulations in OPM-Flow for an ensemble of varying input
arguments.

"""
from __future__ import annotations

import copy
import csv
import logging
import math
import os
import pathlib
import shutil
from collections import OrderedDict
from typing import Any, Optional

import numpy as np
import tensorflow as tf
from ecl.eclfile.ecl_file import open_ecl_file
from ecl.summary.ecl_sum import EclSum
from mako import exceptions
from mako.template import Template

from pyopmnearwell.utils import units
from pyopmnearwell.utils.formulas import area_squaredcircle, pyopmnearwell_correction
from pyopmnearwell.utils.inputvalues import readthefirstpart, readthesecondpart
from pyopmnearwell.utils.writefile import reservoir_files

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dirname = pathlib.Path(__file__).parent

FLAGS = (
    " --linear-solver-reduction=1e-5 --relaxed-max-pv-fraction=0"
    + " --ecl-enable-drift-compensation=0 --newton-max-iterations=50"
    + " --newton-min-iterations=5 --tolerance-mb=1e-7 --tolerance-wells=1e-1"
    + " --relaxed-well-flow-tol=1e-3 --use-multisegment-well=false --enable-tuning=true"
    + " --enable-opm-rst-file=true --linear-solver=cprw"
    + " --enable-well-operability-check=false"
    + " --min-time-step-before-shutting-problematic-wells-in-days=1e-1"
)


def create_ensemble(
    runspecs: dict[str, Any], efficient_sampling: Optional[list[str]] = None
) -> list[dict[str, Any]]:
    """Create an ensemble.

    Note: It is assumed that the user provides the variables in the correct units for
    pyopmnearwell.

    Args:
        runspecs (dict[str, Any]): Dictionary with at least the following keys:
            - "npoints": Maximum number of ensemble members.
            - "variables": ``dict`` containing the run Args vary within the
              ensemble. The key specifies the variable name (needs to be identical to
              the variable name in the ``*.mako`` file that is passed to
              ``setup_ensemble``) and the value is a tuple ``(min, max, npoints)`` with
              the min. and max. values for the variable and the number of samples
              generated for this variable. The samples are taken from a uniform
              distribution in the interval :math:`[min, max]`.
            - "constants": ``dict`` containing the run Args that are constant for
              all ensemble members.
        efficient_sampling (Optional[list[str]], optional): List containing the names of
            variables that should be sampled instead of fully meshed and then sampled.
            This is faster and avoids memory overload for higher dimensional
            combinations of variables. E.g., when creating an ensemble with varying
            vertical permeabilities. Only 10 layers with 10 samples generate a grid of
            10^10 values. By sampling directly instead of generating the grid first, it
            is possible to deal with the complexity.

    Note: The ensemble is generated as the cartesian product of all variable ranges. The
        total number of ensemble members is thus the product of all individual
        ``npoints``. If ``runspecs["npoints"]`` is lower than the product, a random
        sample of size ``runspecs["npoints"]`` of the full ensemble is returned.

    Returns:
        ensemble (list[dict[str, Any]]): List containing a dict with the specified
            variable values for each ensemble member.

    Raises:
        ValueError: If ``runspecs["npoints"]`` is larger than the number of generated
            ensemble members.

    """
    if efficient_sampling is None:
        efficient_sampling = []

    variables: dict[str, np.ndarray] = OrderedDict()

    # Generate random value ranges for all variables.
    logger.info("Generating value ranges for all variables")
    for variable, (min_val, max_val, npoints) in runspecs["variables"].items():
        if variable.startswith("PERM"):
            # Generate a log uniform distribution for permeabilities.
            variables[variable] = np.exp(
                np.random.uniform(math.log(min_val), math.log(max_val), npoints)
            )
        else:
            # Generate a uniform distribution for all other variables.
            variables[variable] = np.random.uniform(min_val, max_val, npoints)
    constants: dict[str, float] = runspecs["constants"]

    # Differentiate between variables whose data ranges are sampled memory efficiently
    # and then added to the ensemble and variables whose data ranges are fully meshed
    # together and then added to the ensemble.
    # NOTE: At the end, the ensemble gets sampled again if it is too large.
    variables_to_sample: dict[str, np.ndarray] = OrderedDict(
        {
            variable: values
            for variable, values in variables.items()
            if variable in efficient_sampling
        }
    )
    variables_to_mesh: dict[str, np.ndarray] = OrderedDict(
        {
            variable: values
            for variable, values in variables.items()
            if variable not in efficient_sampling
        }
    )
    logger.info(
        f"Sampling the following variables individually: {variables_to_sample.keys}"
    )
    logger.info(
        f"Meshing the following variables and sampling afterwards: {variables_to_mesh.keys}"
    )

    # Mesh/sample all values to get the ensemble and put the values back into a
    # dictionary.
    meshed_variables: list[np.ndarray] = [
        array.flatten()
        for array in np.meshgrid(*variables_to_mesh.values(), indexing="ij")
    ]
    if len(variables_to_sample) > 0:
        sampled_variables: np.ndarray | list = memory_efficient_sample(
            np.array(list(variables_to_sample.values())),
            num_members=runspecs["npoints"],
        )
    else:
        sampled_variables = []

    ensemble: list[dict[str, float]] = []
    for values in zip(*meshed_variables, *sampled_variables):
        member: dict[str, Any] = copy.deepcopy(constants)
        member.update(
            {
                (list(variables_to_mesh.keys()) + list(variables_to_sample.keys()))[
                    i
                ]: value
                for i, value in enumerate(values)
            }
        )
        ensemble.append(member)

    # Sample a subset of the ensemble if the ensemble size is larger than wanted.
    ensemble_size: int = np.prod(
        [npoints for _, __, npoints in runspecs["variables"].values()]
    )
    if runspecs["npoints"] < ensemble_size:
        logger.info(
            "Sample size is larger than ensemble size. Randomly selecting a subset"
        )

        idx = np.random.randint(
            len(ensemble),
            size=runspecs["npoints"],
        )
        ensemble = list(map(ensemble.__getitem__, idx))
    elif runspecs["npoints"] > ensemble_size:
        raise ValueError(
            f"runspecs['npoints']={runspecs['npoints']} is larger than the"
            + f" ensemble_size={ensemble_size} generated from the variables."
        )

    logger.info("Created ensemble")

    return ensemble


def memory_efficient_sample(variables: np.ndarray, num_members: int) -> np.ndarray:
    """Sample all variables individually.

    Note: Requires that all variables arrays have the same length.

    Args:
        variables (np.ndarray), (``shape=(num_variables, len_variables)``): _description_
        num_members (int): _description_

    Returns:
        np.ndarray (``shape=()``):

    """
    indices: np.ndarray = np.random.randint(
        0, variables.shape[-1], size=(variables.shape[0], num_members)
    )
    return variables[np.arange(variables.shape[0])[..., None], indices]


def setup_ensemble(
    ensemble_path: pathlib.Path,
    ensemble: list[dict[str, Any]],
    makofile: str | pathlib.Path,
    recalc_grid: bool = False,
    recalc_tables: bool = False,
    recalc_sections: bool = False,
) -> None:
    """Create a deck file for each ensemble member.

    Args:
        ensemble_path (pathlib.Path): The path to the ensemble directory.
        ensemble (list[dict[str, Any]]): A list of dictionaries containing the
            parameters for each ensemble member. Usually generated by
            ``create_ensemble``.
        makofile (str | pathlib.Path): The path to the Mako template file for the
            pyopmnearwell deck for ensemble members.
        recalc_grid (bool, optional): Whether to recalculate ``GRID.INC`` for each
            ensemble member. Defaults to False.
        recalc_tables (bool, optional): Whether to recalculate ``TABLES.INC`` for each
            ensemble member. Defaults to False.
        recalc_sections (bool, optional): Whether to recalculate ``GEOLOGY.INC`` and
            ``REGIONS.INC`` for each ensemble member. Defaults to False.
    Raises:
        Exception: If there is an error rendering the Mako template.

    Returns:
        None

    """
    # Ensure ``ensemble_path`` is a ``Path`` object.
    ensemble_path = pathlib.Path(ensemble_path)

    logger.info(f"Filling templates for {len(ensemble)} members")
    mytemplate: Template = Template(filename=str(makofile))
    for i, member in enumerate(ensemble):
        try:
            filledtemplate = mytemplate.render(**member)
        except Exception as error:
            print(exceptions.text_error_template().render())
            raise error

        (ensemble_path / f"runfiles_{i}").mkdir(exist_ok=True)
        (ensemble_path / f"runfiles_{i}" / "preprocessing").mkdir(exist_ok=True)
        (ensemble_path / f"runfiles_{i}" / "jobs").mkdir(exist_ok=True)

        lol = []
        for row in csv.reader(filledtemplate.split("\n"), delimiter="#"):
            lol.append(row)
        dic, index = readthefirstpart(
            lol,
            {
                "exe": ensemble_path / "..",
                "pat": dirname / "..",  # Path to pyopmnearwell.
                "fol": pathlib.Path(ensemble_path.name) / f"runfiles_{i}",
            },
        )
        dic = readthesecondpart(lol, dic, index)
        dic.update({"runname": f"RUN_{i}"})
        # Always calculate geology, grid, tables, etc. for the first ensemble member.
        if i == 0:
            reservoir_files(dic)
        else:
            reservoir_files(
                dic,
                recalc_grid=recalc_grid,
                recalc_tables=recalc_tables,
                recalc_sections=recalc_sections,
                inc_folder=pathlib.Path("..") / ".." / "runfiles_0" / "preprocessing",
            )
    # pyopmnearwell creates these unneeded folders, so we remove them.
    try:
        shutil.rmtree(ensemble_path / "preprocessing")
        shutil.rmtree(ensemble_path / "jobs")
    except FileNotFoundError:
        pass
    logger.info(f"Filled templates for {len(ensemble)} members")


def run_ensemble(
    flow_path: str | pathlib.Path,
    ensemble_path: pathlib.Path,
    runspecs: dict[str, Any],
    ecl_keywords: list[str],
    init_keywords: list[str],
    summary_keywords: list[str],
    num_report_steps: Optional[int] = None,
) -> dict[str, Any]:
    """Run OPM flow for each ensemble member and store data.

    Args:
        flow_path (_type_): _description_
        ensemble_path (pathlib.Path): _description_
        runspecs (dict[str, Any]): _description_
        ecl_keywords (list[str]): _description_
        init_keywords (list[str]): _description_
        summary_keywords (list[str]): _description_
        num_report_steps (Optional[int], optional): Disregard an ensemble simulation, if
            it did not run to the last report step. Defaults to None.

    Returns:
        dict[str, Any]: _description_

    """
    # Ensure ``ensemble_path`` is a ``Path`` object.
    ensemble_path = pathlib.Path(ensemble_path)

    data: dict = {
        keyword: [] for keyword in ecl_keywords + init_keywords + summary_keywords
    }
    num_disregarded_runs: int = 0

    for i in range(round(runspecs["npoints"] / runspecs["npruns"])):
        command = " ".join(
            [
                f"{flow_path}"
                + f" {ensemble_path / f'runfiles_{j}' / 'preprocessing' / f'RUN_{j}.DATA'}"
                + f" --output-dir={ensemble_path / f'results_{j}'}"
                + f" {FLAGS} & "
                for j in range(runspecs["npruns"] * i, runspecs["npruns"] * (i + 1))
            ]
        )
        os.system(command + "wait")
        for j in range(runspecs["npruns"] * i, runspecs["npruns"] * (i + 1)):
            simulation_finished: bool = True

            with open_ecl_file(
                str(ensemble_path / f"results_{j}" / f"RUN_{j}.UNRST")
            ) as ecl_file:
                # Skip result, if the simulation did not run to the last time step.
                if (
                    num_report_steps is not None
                    and ecl_file.num_report_steps() < num_report_steps
                ):
                    simulation_finished = False

                # Check again if the simulation data is available for all time steps.
                # It seems that sometimes the keyword array has zero report steps, even
                # though `ecl_file.num_report_steps()` is nonzero.
                member_data: dict[str, np.ndarray] = {}
                for keyword in ecl_keywords:
                    # Append the data corresponding to the keyword for all report steps
                    # and cells. Disregard the zeroth time step.
                    member_data[keyword] = np.array(ecl_file.iget_kw(keyword))[1:, ...]
                    if (
                        num_report_steps is not None
                        and member_data[keyword].shape[0] < num_report_steps
                    ):
                        simulation_finished = False

                    # Disregard the result if an `inf` value is returned.
                    elif np.any(np.isinf(member_data[keyword])):
                        simulation_finished = False

            # Only append data if the simulation finished.
            if simulation_finished:
                for keyword in ecl_keywords:
                    data[keyword].append(member_data[keyword])

                with open_ecl_file(
                    ensemble_path / f"results_{j}" / f"RUN_{j}.INIT"
                ) as init_file:
                    for keyword in init_keywords:
                        # Append the data corresponding to the keyword for all cells.
                        data[keyword].append(np.array(init_file.iget_kw(keyword)))

                summary_file: EclSum = EclSum(
                    ensemble_path / f"results_{j}" / f"RUN_{j}.SMSPEC"
                )
                for keyword in summary_keywords:
                    # Append the data corresponding to the keyword for all report steps
                    # (not for all time steps). The ``*.SMSPEC`` file does not include
                    # the zeroth report step. Add a dimension to make it
                    # broadcastable to data from the ``*.UNRST`` and ``*.INIT`` files.
                    data[keyword].append(
                        np.array(
                            summary_file.get_values(keyword, report_only=True)[
                                ..., None
                            ]
                        )
                    )
                # NOTE: There does not seem to be a way to close an ``EclSum`` object.
                # Also, there is no context manager.

            else:
                num_disregarded_runs += 1
                logger.info(f"Disregarded ensemble run {j}")
            # Remove the run files and result folder (except for the first one that
            # remains to check if everything went right).
            if j > 0:
                shutil.rmtree(ensemble_path / f"results_{j}")
                shutil.rmtree(ensemble_path / f"runfiles_{j}")
        logger.info(f"Disregarded {num_disregarded_runs} of {runspecs['npoints']} runs")

    return data


def calculate_radii(
    gridfile: pathlib.Path,
    num_cells: int = 400,
    # num_dims: int = 1,
    return_outer_inner: bool = False,
    triangle_grid: bool = False,
    theta: float = math.pi / 3,
) -> np.ndarray | tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculates the radii of the cells in a grid grom a given .

    Args:
        gridfile (str | pathlib.Path): Path to the file containing the grid.
        num_cells (int, optional): Number of cells in the grid. Defaults to 400.
        num_dims (int, optional): Number of dimensions of the grid. Defaults to 1.
        return_outer_inner (bool, optional): Whether to return the inner and outer radii
            in addition to the average radii. Defaults to False.
        triangle_grid (bool, optional): Whether the grid is a triangle grid. If
            True, transform altitudes of the triangle grid to radii of a raidal grid
            with equal solution. Defaults to False.
        theta (float, optional): Angle between the horizontal axis and the edge of the
            triangle grid. Defaults to ``math.pi/3``.


    Returns:
        np.ndarray | tuple[np.ndarray, np.ndarray, np.ndarray]: If return_outer_inner is
            False, returns an array of the average radii of the cells.

            If return_outer_inner is True, returns a tuple containing the array of
            average radii, the array of inner radii, and the array of outer radii.

    Raises:
        AssertionError: If the number of lines in the grid file is not equal to
            num_cells + 1.

    """
    # Ensure ``gridfile`` is a ``Path`` object.
    gridfile = pathlib.Path(gridfile)

    with gridfile.open("r", encoding="utf-8") as radii_file:
        lines: list[str] = radii_file.readlines()[9 : 10 + num_cells]
        assert len(lines) == num_cells + 1
        radii: np.ndarray = np.array(
            list(
                map(
                    lambda x: float(x.strip("\n").split()[0]),
                    lines,
                )
            )
        )
        if triangle_grid:
            radii *= pyopmnearwell_correction(theta)
    inner_radii: np.ndarray = radii[:-1]
    outer_radii: np.ndarray = radii[1:]
    radii_t: np.ndarray = (inner_radii + outer_radii) / 2  # unit: [m]
    if return_outer_inner:
        return radii_t, inner_radii, outer_radii
    return radii_t


def calculate_WI(
    data: dict[str, Any],
    runspecs: dict[str, Any],
    num_zcells: int,
) -> tuple[np.ndarray, list[int]]:
    r"""Calculate the well index (WI) for a given dataset.

    The well index (WI) is calculated using the following formula:

    .. math::
        WI = \frac{q}{{p_w - p_{gb}}}

    Note: In 3D this will more probably than not fail.

    Args:
        data (dict[str, Any]): Data generated by ``run_ensemble``.
        runspecs (dict[str, Any]): Must contain a key "INJECTION_RATE_PER_SECOND". Unit
        [m^3/s].

    Returns:
        WI_array (numpy.ndarray): ``shape=(,num_cells - 1)``
            An array of well index values for each data point in the dataset. In the
            correct unit for OPM. Unit [m^4*s/kg].
        failed_indices (list[int]): Indices for the ensemble members where WI could not
        be computed. E.g., if the simmulation went wrong and the pressure difference is
        zero.

    Raises:
        ValueError: If no data is found for the 'pressure' keyword in the dataset.
    """
    # Transform pressure values from [bar] (unit in *.UNRST files) to [Pa] (unit to
    # calculate the WI and internally used by OPM).
    pressure_data = (
        np.array(data["PRESSURE"]) * units.BAR_TO_PASCAL
    )  # ``shape=(runspecs["npoints"], num_time_data - 1, num_grid_cell_data)``;
    # unit [Pa]
    if len(pressure_data) == 0:
        raise ValueError("No data found for the 'pressure' keyword.")

    # Calculate WI for each ensemble member.
    WI_values: list[np.ndarray] = []
    failed_indices: list[int] = []
    for i, member_pressure_data in enumerate(pressure_data):
        p_w = member_pressure_data[
            ..., 0 :: int(member_pressure_data.shape[-1] / num_zcells)
        ]  # Bottom hole pressure extracted at the well blocks.
        p_gb = np.delete(
            member_pressure_data,
            np.arange(
                0,
                member_pressure_data.shape[-1],
                int(member_pressure_data.shape[-1] / num_zcells),
            ),
            axis=-1,
        )  # Cell pressures of all but the well blocks.
        try:
            if "INJECTION_RATE_PER_SECOND" in runspecs["constants"]:
                # Injection rate is constant for all ensemble members.
                WI = runspecs["constants"]["INJECTION_RATE_PER_SECOND"] / (
                    np.tile(p_w, int(member_pressure_data.shape[-1] / num_zcells) - 1)
                    - p_gb
                )  # ``shape=(runspecs["npoints"], num_time_data - 1, num_grid_cell_data)``;
                # unit [m^4*s/kg]
            elif "INJECTION_RATE_PER_SECOND" in data:
                # Get i-th injection rate in the ensemble.
                WI = data["INJECTION_RATE_PER_SECOND"][i] / (
                    np.tile(p_w, int(member_pressure_data.shape[-1] / num_zcells) - 1)
                    - p_gb
                )  # ``shape=(runspecs["npoints"], num_time_data - 1, num_grid_cell_data)``;
                # unit [m^4*s/kg]
            if np.any(np.isnan(WI)):
                raise ValueError("WI is nan.")
            WI_values.append(WI)
        except ValueError:
            failed_indices.append(i)

    return (
        np.array(WI_values),
        failed_indices,
    )  # ``shape=(,num_cells - 1)``; ; unit [m^4*s/kg]


def extract_features(
    data: dict[str, Any],
    keywords: list[str],
    keyword_scalings: Optional[dict[str, float]] = None,
) -> np.ndarray:
    r"""Extract features into a numpy array.

    Note: The features are in the units used in ``*.UNRST`` and ``*.SMSPEC`` files. The
    user is responsible for transforming them to the units needed. This may depend on
    various factors such as the mode OPM will run in. In particular, pressure is in
    [bar].
    Some units for common quantities:
    - Pressure: [bar]
    - Temperate: [°C]
    - Saturation: [unitless]
    - Time: []

    Args:
        data (dict[str, Any]): Data generated by ``run_ensemble``.
        keywords (list[str]): Keywords to extract. The features will be in the order of
        the keywords.
        keyword_scalings (Optional[dict[str, float]]): Scalings for the features.

    Returns:
        feature_array: (numpy.ndarray): ``shape=(,num_cells - 1)``
            An array of input features each data point in the dataset.

    Raises:
        ValueError: If no data is found for the 'pressure' keyword in the dataset.

    """
    if keyword_scalings is None:
        keyword_scalings = {}
    features: list[np.ndarray] = []
    for keyword in keywords:
        feature: np.ndarray = np.array(
            data[keyword]
        )  # ``shape=(ensemble_size, num_report_steps, num_cells)``
        if keyword == "TEMPERATURE":
            feature += keyword_scalings.get(keyword, 0.0)
        else:
            feature *= keyword_scalings.get(keyword, 1.0)
        features.append(feature)

    # Broadcast all features to the same shape
    broadcasted_shape = np.broadcast_shapes(*[feature.shape for feature in features])
    features = [np.broadcast_to(feature, broadcasted_shape) for feature in features]

    return np.stack(
        features, axis=-1
    )  # ``shape=(ensemble_size, num_report_steps, num_cells, num_features)``


def integrate_fine_scale_value(
    radial_values: np.ndarray,
    radii: np.ndarray,
    block_sidelength: float,
    axis: int = -1,
) -> np.ndarray:
    """Integrate a fine scale value across all radial cells lying in a square grid
    block.

    Args:
        radial_values (np.ndarray): Cell values for the radial cells.
        radii (np.ndarray): Array of radii for inner and outer radius of the radial
        cells.
        block_sidelength (float): The sidelength of the square grid block.
        axis (int): Axis to integrate along.

    Returns:
        float: The integrated value of fine-scale data.

    """
    if radial_values.shape[0] > 0:
        assert radial_values.shape[axis] == radii.shape[0] - 1
    else:
        return np.zeros_like(radial_values)

    # Ignore mypy complaining. ``area_squaredcircle`` returns an np.ndarray in this
    # case. This can be removed, once the typing in ``formulas.py`` is more strict.
    cell_areas: np.ndarray = area_squaredcircle(  # type: ignore
        radii[1::], block_sidelength
    ) - area_squaredcircle(radii[:-1:], block_sidelength)
    return np.sum(radial_values * cell_areas, axis=axis)


def store_dataset(
    features: np.ndarray, targets: np.ndarray, savepath: str | pathlib.Path
) -> pathlib.Path:
    """Store a TensorFlow dataset given by to tensors.

    Args:
        features (np.ndarray): Features of the dataset.
        targets (np.ndarray): Targets of the dataset.
        savepath (str | pathlib.Path): Folder where the dataset should be saved.

    Returns:
        pathlib.Path: Savepath of the dataset

    """
    ds = tf.data.Dataset.from_tensor_slices((features, targets))
    ds.save(str(savepath))
    return pathlib.Path(savepath)
