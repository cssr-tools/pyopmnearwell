""""Run nearwell CO2 storage simulations in OPM-Flow for an ensemble of varying initial
pressures and construct a dataset containing initial reservoir pressures and equivalent
well-radii as features and well indices as targets.

Features:
    1. pressure [Pa]: Measured at the final time step at the equivalent well radius.
    2. radius [m]: Gives the equivalent well radius.

Targets:
    1. WI [m*s]: Calculated at the given radius.

Note: The wellbore radius, permeability, density and viscosity are fixed.


"""
from __future__ import annotations

import logging
import math
import os
import shutil

import constants
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from ecl.eclfile.ecl_file import open_ecl_file
from mako.template import Template

import pyopmnearwell.utils.units as units
from pyopmnearwell.utils.formulas import peaceman_WI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


run_name: str = "ensemble_runs"
dirpath: str = os.path.dirname(os.path.realpath(__file__))
os.makedirs(os.path.join(dirpath, run_name), exist_ok=True)
ensemble_path = os.path.join(dirpath, run_name)

shutil.copyfile(
    os.path.join(dirpath, "TABLES.INC"),
    os.path.join(dirpath, run_name, "TABLES.INC"),
)
shutil.copyfile(
    os.path.join(dirpath, "CAKE.INC"),
    os.path.join(dirpath, run_name, "CAKE.INC"),
)

# Create pressure ensemble.
init_pressures: np.ndarray = np.random.uniform(
    70, 120, constants.constants.NPOINTS
)  # unit: bar

FLOW = "/home/peter/Documents/2023_CEMRACS/opm/build/opm-simulators/bin/flow"
FLAGS = (
    " --linear-solver-reduction=1e-5 --relaxed-max-pv-fraction=0"
    + " --ecl-enable-drift-compensation=0 --newton-max-iterations=50"
    + " --newton-min-iterations=5 --tolerance-mb=1e-7 --tolerance-wells=1e-5"
    + " --relaxed-well-flow-tol=1e-5 --use-multisegment-well=false --enable-tuning=true"
    + " --enable-opm-rst-file=true --linear-solver=cprw"
    + " --enable-well-operability-check=false"
    + " --min-time-step-before-shutting-problematic-wells-in-days=1e-99"
)

# Create a deck file for each ensemble member
mytemplate = Template(filename=os.path.join(dirpath, "RESERVOIR.mako"))
for i, pressure in enumerate(init_pressures):
    var = {
        "permeability_x": constants.PERMEABILITY,
        "init_pressure": pressure,
        "temperature": constants.TEMPERATURE,
        "injection_rate": constants.INJECTION_RATE,
    }
    filledtemplate = mytemplate.render(**var)
    with open(
        os.path.join(ensemble_path, f"RESERVOIR{i}.DATA"),
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)  # type: ignore

# Store final grid cell pressures for each ensemble member.
pressures: list[np.ndarray] = []

# Run OPM flow for each ensemble member.
for i in range(round(constants.NPOINTS / constants.NPRUNS)):
    os.system(
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{constants.NPRUNS*i}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{constants.NPRUNS*i}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{constants.NPRUNS*i+1}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{constants.NPRUNS*i+1}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{constants.NPRUNS*i+2}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{constants.NPRUNS*i+2}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{constants.NPRUNS*i+3}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{constants.NPRUNS*i+3}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{constants.NPRUNS*i+4}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{constants.NPRUNS*i+4}')} {FLAGS} & wait"
    )
    for j in range(constants.NPRUNS):
        with open_ecl_file(
            os.path.join(
                ensemble_path,
                f"results{constants.NPRUNS*i+j}",
                f"RESERVOIR{constants.NPRUNS*i+j}.UNRST",
            )
        ) as ecl_file:
            # The pressure array has shape ``[number_report_steps, number_cells]``
            pressures.append(np.array(ecl_file.iget_kw("PRESSURE"))[-1])

        # Remove the run files and result folder (except for the first one).
        if constants.NPRUNS * i + j > 0:
            shutil.rmtree(
                os.path.join(ensemble_path, f"results{constants.NPRUNS*i+j}"),
            )
            os.remove(
                os.path.join(ensemble_path, f"RESERVOIR{constants.NPRUNS*i+j}.DATA")
            )
os.remove(os.path.join(ensemble_path, f"TABLES.INC"))
os.remove(os.path.join(ensemble_path, f"CAKE.INC"))


# Create feature tensor.
# Calculate cell center radii.
with open(os.path.join(dirpath, "CAKE.INC"), "r") as radii_file:
    # Calculate the radius of the midpoint of each cell
    lines: list[str] = radii_file.readlines()[9:410]
    assert len(lines) == 401
    radii: np.ndarray = np.array(
        list(
            map(
                lambda x: math.sqrt(
                    float(x.strip("\n").split()[0]) ** 2
                    + float(x.strip("\n").split()[1]) ** 2
                ),
                lines,
            )
        )
    )
    inner_radii: np.ndarray = radii[:-1]
    outer_radii: np.ndarray = radii[1:]
    radii_t: np.ndarray = (inner_radii + outer_radii) / 2  # unit: [m]
# Truncate the well cells and cells in the close proximity, as well as the outermost
# cell (pore-volume) to sanitize the dataset (WI close to cell behaves weirdly).
radii_t = radii_t[4:-1]
assert radii_t.shape == (395,)


pressures_t = (
    np.array(pressures) * units.BAR_TO_PASCAL
)  # ``shape=(constants.NPOINTS, 400`, unit: [Pa]


features = np.stack(
    [pressures_t[:, 4:-1].flatten(), np.tile(radii_t, constants.NPOINTS)], axis=-1
)  # ``shape=(constants.NPOINTS * 395, 2)``

# Calculate the well indices from injection rate, cell pressures and bhp.
# Get the pressure value of the innermost cell, which equals the bottom hole pressure.
bhp_t: np.ndarray = pressures_t[:, 0]

# Truncate the cell pressures the same way the radii were truncated.
WI_t: np.ndarray = (
    constants.INJECTION_RATE
    * units.Q_per_day_to_Q_per_seconds
    / (bhp_t[..., None] - pressures_t[:, 4:-1])
)  # unit: m*s; ``shape=(constants.NPOINTS, 395, 1)``

# Store the features: pressures, radii, and targets: WI as a dataset.
ds = tf.data.Dataset.from_tensor_slices((features, WI_t.flatten()[..., None]))
ds.save(os.path.join(ensemble_path, "pressure_radius_WI"))

# Plot pressure, distance - WI relationship vs Peaceman model
WI_analytical = np.vectorize(peaceman_WI)(
    constants.PERMEABILITY * units.MILIDARCY_TO_M2,
    radii_t,
    constants.WELL_RADIUS,
    constants.DENSITY,
    constants.VISCOSITY,
)

features = np.reshape(features, (constants.NPOINTS, 395, 2))

for feature, target in list(zip(features, WI_t))[:5]:
    plt.scatter(
        feature[..., 1].flatten()[::5],
        target.flatten()[::5],
        label="data",
    )
    plt.plot(
        feature[..., 1],
        WI_analytical,
        label="Peaceman",
    )
    plt.legend()
    plt.title(rf"$p={feature[20][0]:.3e}$ Pa at $r={feature[20][1]:.2f}$ [m]")
    plt.xlabel(r"$r$ [m]")
    plt.ylabel(r"$WI$ [ms]")
    plt.savefig(
        os.path.join(dirpath, run_name, f"data_vs_Peaceman_p_f{feature[20][0]}.png")
    )
    plt.show()


# Three dimensional plot of permeabilities and radii vs. WI, pressure fixed.
fig = plt.figure()
ax = plt.axes(projection="3d")
ax.plot_surface(
    features[..., 0],
    features[..., 1],
    np.squeeze(WI_t),
    rstride=1,
    cstride=1,
    cmap="viridis",
    edgecolor="none",
)
ax.set_xlabel(r"$p$ [Pa]")
ax.set_ylabel(r"$r$ [m]")
ax.set_title(r"$WI$ [ms]")
plt.savefig(os.path.join(dirpath, run_name, "data_3d.png"))
plt.show()
