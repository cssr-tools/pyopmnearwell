""""Run high-fidelity nearwell simulations in OPM-Flow for an ensemble of varying input
arguments.

"""
from __future__ import annotations

import copy
import csv
import logging
import math
import os
import shutil
from collections import OrderedDict
from typing import Any, Optional

import numpy as np
import tensorflow as tf
from ecl.eclfile.ecl_file import open_ecl_file
from mako import exceptions
from mako.template import Template

import pyopmnearwell.utils.units as units
from pyopmnearwell.utils.inputvalues import readthefirstpart, readthesecondpart
from pyopmnearwell.utils.writefile import reservoir_files

dir = os.path.dirname(__file__)

FLAGS = (
    " --linear-solver-reduction=1e-5 --relaxed-max-pv-fraction=0"
    + " --ecl-enable-drift-compensation=0 --newton-max-iterations=50"
    + " --newton-min-iterations=5 --tolerance-mb=1e-7 --tolerance-wells=1e-5"
    + " --relaxed-well-flow-tol=1e-7 --use-multisegment-well=false --enable-tuning=true"
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
        efficient_sampling (Optional[list[str]]): List containing the names of variables
        that should be sampled instead of fully meshed and then sampled. This is faster
        and avoids memory overload for higher dimensional combinations of variables.
        E.g., when creating an ensemble with varying vertical permeabilities. Only 10
        layers with 10 samples generate a grid of 10^10 values. By sampling directly
        instead of generating the grid first, it is possible to deal with the
        complexity.

    Note: The ensemble is generated as the cartesian product of all variable ranges. The
    total number of ensemble members is thus the product of all individual ``npoints``.
    If ``runspecs["npoints"]`` is lower than the product, a random sample of size
    ``runspecs["npoints"]`` of the full ensemble is returned.

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
    return ensemble


def memory_efficient_sample(variables: np.ndarray, num_members: int) -> np.ndarray:
    """Requires that all variables have the same number of samples.

    Parameters:
        variables (np.ndarray): _description_
        num_members (int): _description_

    Returns:
        _description_
    """
    indices: np.ndarray = np.random.randint(
        0, variables.shape[-1], size=(variables.shape[0], num_members)
    )
    return variables[np.arange(variables.shape[0])[..., None], indices]


def setup_ensemble(
    ensemble_path: str,
    ensemble: list[dict[str, Any]],
    makofile: str,
    recalc_grid: bool = False,
    recalc_tables: bool = False,
    recalc_sections: bool = False,
) -> None:
    """ "Create a deck file for each ensemble member."""
    mytemplate: Template = Template(filename=makofile)
    for i, member in enumerate(ensemble):
        try:
            filledtemplate = mytemplate.render(**member)
        except Exception as error:
            print(exceptions.text_error_template().render())
            raise (error)

        os.makedirs(os.path.join(ensemble_path, f"runfiles_{i}"), exist_ok=True)
        os.makedirs(
            os.path.join(ensemble_path, f"runfiles_{i}", "preprocessing"), exist_ok=True
        )
        os.makedirs(os.path.join(ensemble_path, f"runfiles_{i}", "jobs"), exist_ok=True)

        lol = []
        for row in csv.reader(filledtemplate.split("\n"), delimiter="#"):
            lol.append(row)
        dic, index = readthefirstpart(
            lol,
            {
                "exe": os.path.join(ensemble_path, ".."),
                "pat": os.path.join(dir, ".."),  # Path to pyopmnearwell.
                "fol": os.path.join(os.path.split(ensemble_path)[1], f"runfiles_{i}"),
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
                inc_folder=os.path.join(
                    "..",
                    "..",
                    "runfiles_0",
                    "preprocessing",
                ),
            )
    # pyopmnearwell creates these unneeded folders, so we remove them.
    try:
        shutil.rmtree(os.path.join(ensemble_path, "preprocessing"))
        shutil.rmtree(os.path.join(ensemble_path, "jobs"))
    except FileNotFoundError:
        pass


def run_ensemble(
    flow_path: str,
    ensemble_path: str,
    runspecs: dict[str, Any],
    ecl_keywords: list[str],
    init_keywords: list[str],
    summary_keywords: list[str],
    num_report_steps: Optional[int] = None,
) -> dict[str, Any]:
    """Run OPM flow for each ensemble member and store data.

    Args:
        flow_path (_type_): _description_
        ensemble_path (_type_): _description_
        runspecs (_type_): _description_
        ecl_keywords (_type_): _description_
        init_keywords (_type_): _description_
        summary_keywords (_type_): _description_
        num_report_steps (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    data: dict = {
        keyword: [] for keyword in ecl_keywords + init_keywords + summary_keywords
    }
    for i in range(round(runspecs["npoints"] / runspecs["npruns"])):
        command = " ".join(
            [
                f"{flow_path}"
                + f" {os.path.join(ensemble_path, f'runfiles_{j}', 'preprocessing', f'RUN_{j}.DATA')}"
                + f" --output-dir={os.path.join(ensemble_path, f'results_{j}')}"
                + f" {FLAGS} & "
                for j in range(runspecs["npruns"] * i, runspecs["npruns"] * (i + 1))
            ]
        )
        os.system(command + "wait")
        for j in range(runspecs["npruns"] * i, runspecs["npruns"] * (i + 1)):
            with open_ecl_file(
                os.path.join(ensemble_path, f"results_{j}", f"RUN_{j}.UNRST")
            ) as ecl_file:
                # Skip result, if the simulation did not run to the last time step:
                if (
                    num_report_steps is not None
                    and ecl_file.num_report_steps() < num_report_steps
                ):
                    continue

                for keyword in ecl_keywords:
                    # Append the data corresponding to the keyword for all report steps
                    # and cells.
                    data[keyword].append(np.array(ecl_file.iget_kw(keyword)))
            with open_ecl_file(
                os.path.join(ensemble_path, f"results_{j}", f"RUN_{j}.INIT")
            ) as init_file:
                for keyword in init_keywords:
                    # Append the data corresponding to the keyword for all cells.
                    data[keyword].append(np.array(init_file.iget_kw(keyword)))
            with open_ecl_file(
                os.path.join(ensemble_path, f"results_{j}", f"RUN_{j}.SMSPEC")
            ) as summary_file:
                for keyword in summary_keywords:
                    # Append the data corresponding to the keyword for all report steps.
                    # TODO
                    pass
            # Remove the run files and result folder (except for the first one that
            # remains to check if everything went right).
            if j > 0:
                shutil.rmtree(
                    os.path.join(ensemble_path, f"results_{j}"),
                )
                shutil.rmtree(
                    os.path.join(ensemble_path, f"runfiles_{j}"),
                )
                pass
    return data


def calculate_radii(
    gridfile: str,
    num_dims: int = 1,
) -> np.ndarray:
    with open(gridfile) as radii_file:
        lines: list[str] = radii_file.readlines()[9:410]
        assert len(lines) == 401
        radii: np.ndarray = np.array(
            list(
                map(
                    lambda x: float(x.strip("\n").split()[0]),
                    lines,
                )
            )
        )
    inner_radii: np.ndarray = radii[:-1]
    outer_radii: np.ndarray = radii[1:]
    radii_t: np.ndarray = (inner_radii + outer_radii) / 2  # unit: [m]
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
    # calculate the WI and internally used by OPM). Remove the initial time step.
    pressure_data = (np.array(data["PRESSURE"]) * units.BAR_TO_PASCAL)[
        ..., 1:, :
    ]  # ``shape=(runspecs["npoints"], num_time_data - 1, num_grid_cell_data)``;
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
            WI_values.append(WI)
        except Exception:
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


def store_dataset(features: np.ndarray, targets: np.ndarray, savepath: str) -> None:
    ds = tf.data.Dataset.from_tensor_slices((features, targets))
    ds.save(savepath)


# def plot_WI_2D(
#     features: np.ndarray,
#     WI: np.ndarray,
#     yaxis: Literal["radius", "time"] = "radius",
#     num_plots: int = 3,
# ) -> None:
#     features_reshaped = features.reshape((..., features.shape[-1]))
#     feature_1 = features_reshaped[..., indices[0]]
#     feature_1 = features_reshaped[..., indices[1]]
#     for feature, target in list(zip(features[:3, ...], WI_data[:3, ...])):
#         plt.figure()
#         plt.scatter(
#             radii_t[::5],
#             target[::5],
#             label="data",
#         )
#         plt.plot(
#             radii_t,
#             WI_analytical,
#             label="Peaceman",
#         )
#         plt.legend()
#         plt.title(
#             rf"$p={feature[20][0]:.3e}\,[Pa]$ Peaceman at $r={feature[20][1]:.2f}\,[m]$"
#         )
#         plt.xlabel(r"$r\,[m]$")
#         plt.ylabel(r"$WI\,[m^4\cdot s/kg]$")
#         plt.savefig(
#             os.path.join(
#                 dirpath, run_name, f"data_vs_Peaceman_p_{feature[20][0]:.3e}.png"
#             )
#         )
#         plt.show()


def plot_WI_3D(data: np.ndarray, runspecs: dict[str, Any]) -> None:
    pass
