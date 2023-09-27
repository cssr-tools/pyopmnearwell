""""Run high-fidelity nearwell simulations in OPM-Flow for an ensemble of varying input
arguments.

"""
from __future__ import annotations

import copy
import csv
import logging
import os
import shutil
import subprocess
from collections import OrderedDict
from typing import Any, Literal, Optional

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from ecl.eclfile.ecl_file import open_ecl_file
from mako.template import Template

import pyopmnearwell.utils.units as units
from pyopmnearwell.utils.formulas import peaceman_WI
from pyopmnearwell.utils.inputvalues import readthefirstpart, readthesecondpart
from pyopmnearwell.utils.writefile import reservoir_files

dir = os.path.dirname(__file__)

FLAGS = (
    " --linear-solver-reduction=1e-5 --relaxed-max-pv-fraction=0"
    + " --ecl-enable-drift-compensation=0 --newton-max-iterations=50"
    + " --newton-min-iterations=5 --tolerance-mb=1e-7 --tolerance-wells=1e-5"
    + " --relaxed-well-flow-tol=1e-5 --use-multisegment-well=false --enable-tuning=true"
    + " --enable-opm-rst-file=true --linear-solver=cprw"
    + " --enable-well-operability-check=false"
    + " --min-time-step-before-shutting-problematic-wells-in-days=1e-99"
)


def create_ensemble(runspecs: dict[str, Any]) -> list[dict[str, Any]]:
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
    variables: dict[str, np.ndarray] = OrderedDict()

    # Generate random value ranges for all variables.
    for variable, (min, max, npoints) in runspecs["variables"].items():
        variables[variable] = np.random.uniform(min, max, npoints)
    constants: dict[str, float] = runspecs["constants"]

    # Mesh all values to get the ensemble and put the values back into a dictionary.
    meshed_variables = [
        array.flatten() for array in np.meshgrid(*variables.values(), indexing="ij")
    ]
    ensemble: list[dict[str, float]] = []
    for values in zip(*meshed_variables):
        member: dict[str, Any] = copy.deepcopy(constants)
        member.update(
            {list(variables.keys())[i]: value for i, value in enumerate(values)}
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


def setup_ensemble(
    ensemble_path: str, ensemble: list[dict[str, Any]], makofile: str
) -> None:
    """ "Create a deck file for each ensemble member."""
    template = Template(filename=makofile)
    os.makedirs(os.path.join(ensemble_path, "preprocessing"), exist_ok=True)
    os.makedirs(os.path.join(ensemble_path, "jobs"), exist_ok=True)
    for i, member in enumerate(ensemble):
        filledtemplate = template.render(**member)
        lol = []
        for row in csv.reader(filledtemplate.split("\n"), delimiter="#"):
            lol.append(row)
        dic, index = readthefirstpart(
            lol,
            {
                "exe": os.path.join(ensemble_path, ".."),
                "pat": os.path.join(dir, ".."),  # Path to pyopmnearwell.
                "fol": os.path.split(ensemble_path)[1],
            },
        )
        dic = readthesecondpart(lol, dic, index)
        dic.update({"runname": f"RUN_{i}"})
        # Only recalculate geology, grid, tables, etc. for the first ensemble member.
        if i == 0:
            reservoir_files(dic)
        else:
            reservoir_files(
                dic, recalc_grid=False, recalc_tables=False, recalc_sections=False
            )


def run_ensemble(
    flow_path: str,
    ensemble_path: str,
    runspecs: dict[str, Any],
    ecl_keywords: list[str],
    summary_keywords: list[str],
) -> dict[str, Any]:
    """Run OPM flow for each ensemble member and store data."""
    data: dict = {keyword: [] for keyword in ecl_keywords + summary_keywords}
    for i in range(round(runspecs["npoints"] / runspecs["npruns"])):
        command_lst = [
            f"{flow_path}"
            + f" {os.path.join(ensemble_path, 'preprocessing', f'RUN_{j}.DATA')}"
            + f" --output-dir={os.path.join(ensemble_path, f'results_{j}')}"
            + f" {FLAGS} & "
            for j in range(runspecs["npruns"] * i, runspecs["npruns"] * (i + 1))
        ]

        command = " ".join(
            [
                f"{flow_path}"
                + f" {os.path.join(ensemble_path, 'preprocessing', f'RUN_{j}.DATA')}"
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
                for keyword in ecl_keywords:
                    # Append the data corresponding to the keyword for all report steps
                    # and cells.
                    data[keyword].append(np.array(ecl_file.iget_kw(keyword)))
            with open_ecl_file(
                os.path.join(ensemble_path, f"results_{j}", f"RUN_{j}.SMSPEC")
            ) as ecl_file:
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
                os.remove(os.path.join(ensemble_path, "preprocessing", f"RUN_{j}.DATA"))

    # Clean up:
    # Remove all run files except for `GRID.INC`, which is needed to calculate radii.
    for file in ["TABLES", "CAKE", "GEOLOGY", "MULTPV", "REGIONS"]:
        try:
            os.remove(os.path.join(ensemble_path, "preprocessing", f"{file}.INC"))
        except FileNotFoundError:
            pass
    shutil.rmtree(os.path.join(ensemble_path, "jobs"))
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
    num_dims: int = 1,
) -> np.ndarray:
    r"""Calculate the well index (WI) for a given dataset.

    The well index (WI) is calculated using the following formula:

    .. math::
        WI = \frac{q}{{p_w - p_{gb}}}

    Args:
        data (dict[str, Any]): Data generated by ``run_ensemble``.
        runspecs (dict[str, Any]): Must contain a key "INJECTION_RATE_PER_SECOND". Unit
        [m^3/s].

    Returns:
        WI_array (numpy.ndarray): ``shape=(,num_cells - 1)``
            An array of well index values for each data point in the dataset. In the
            correct unit for OPM. Unit [m^4*s/kg].

    Raises:
        ValueError: If no data is found for the 'pressure' keyword in the dataset.
    """
    # Transform pressure values from [bar] (unit in *.UNRST files) to [Pa] (unit to
    # calculate the WI and internally used by OPM).
    pressure_data = (
        np.array(data["PRESSURE"]) * units.BAR_TO_PASCAL
    )  # ``shape=(runspecs.NPOINTS, num_report_steps/5, 400)``; unit [Pa]
    if len(pressure_data) == 0:
        raise ValueError("No data found for the 'pressure' keyword.")

    # Calculate WI for each ensemble member
    WI_values = []
    for i, datapoint in enumerate(pressure_data):
        p_w = datapoint[..., 0][
            ..., None
        ]  # Bottom hole pressure extracted at the first cell.
        p_gb = datapoint[..., 1:]  # Cell pressures of all but the well block.
        if "INJECTION_RATE_PER_SECOND" in runspecs["constants"]:
            # Injection rate is constant for all ensemble members.
            WI = runspecs["constants"]["INJECTION_RATE_PER_SECOND"] / (
                p_w - p_gb
            )  # ``shape=(...,num_cells - 1)``; unit [m^4*s/kg]
        elif "INJECTION_RATE_PER_SECOND" in data:
            # Get i-th injection rate in the ensemble.
            WI = data["INJECTION_RATE_PER_SECOND"][i] / (
                p_w - p_gb
            )  # ``shape=(...,num_cells - 1)``; unit [m^4*s/kg]

        WI_values.append(WI)

    return np.array(WI_values)  # ``shape=(,num_cells - 1)``; ; unit [m^4*s/kg]


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
        # Truncate the data at the well cell.
        feature: np.ndarray = np.array(data[keyword])[
            ..., 1:
        ]  # ``shape=(ensemble_size, num_report_steps, num_cells - 1)``
        if keyword == "TEMPERATURE":
            feature += keyword_scalings.get(keyword, 0.0)
        else:
            feature *= keyword_scalings.get(keyword, 1.0)
        features.append(feature)
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
