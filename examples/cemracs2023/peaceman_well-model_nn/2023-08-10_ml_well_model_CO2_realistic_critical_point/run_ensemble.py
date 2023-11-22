""""Run nearwell CO2 storage simulations in OPM-Flow for an ensemble of varying initial
pressures and construct a dataset containing initial reservoir pressures and radii as
features and well indices as targets.

Features:
    1. pressure [bar]
    2. radius [m]

Targets:
    1. WI [m*s]

"""

from __future__ import annotations

import logging
import math
import os
import shutil

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

# Set run specs and parameters for ensemble simulations
npoints, npruns = 600, 5
# Create pressure ensemble and convert to [m^2].
init_pressures: np.ndarray = np.random.uniform(70, 75, npoints)  # unit: bar
PERMEABILITY: float = 1e-12 * units.M2_TO_MILIDARCY  # unit: mD
TEMPERATURE: float = 30.9780  # unit: °C
INJECTION_RATE: float = 5.352087e3  # unit: [kg/d]
X: float = 2.500000e-01  # Outer coordinates of first cell.
Y: float = -1.443376e-01
WELL_RADIUS: float = math.sqrt(X**2 + Y**2)  # unit: [m]; Fixed during training.
DENSITY: float = (
    12.9788  # unit: kg/m^3; for 72 bar, 30.9780 °C. Is this at surface conditions or not?
)
VISCOSITY: float = 1.52786e-05  # unit: Pa*s; for 72 bar, 30.9780 °C

FLOW = "flow"
FLAGS = (
    " --linear-solver-reduction=1e-5 --relaxed-max-pv-fraction=0"
    + " --enable-drift-compensation=0 --newton-max-iterations=50"
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
        "permeability_x": PERMEABILITY,
        "init_pressure": pressure,
        "temperature": TEMPERATURE,
        "injection_rate": INJECTION_RATE,
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
for i in range(round(npoints / npruns)):
    os.system(
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{npruns*i}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{npruns*i}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{npruns*i+1}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{npruns*i+1}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{npruns*i+2}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{npruns*i+2}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{npruns*i+3}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{npruns*i+3}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{npruns*i+4}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{npruns*i+4}')} {FLAGS} & wait"
    )
    for j in range(npruns):
        with open_ecl_file(
            os.path.join(
                ensemble_path, f"results{npruns*i+j}", f"RESERVOIR{npruns*i+j}.UNRST"
            )
        ) as ecl_file:
            # The pressure array has shape ``[number_report_steps, number_cells]``
            pressures.append(np.array(ecl_file.iget_kw("PRESSURE"))[-1])

        # Remove the run files and result folder (except for the first one).
        if npruns * i + j > 0:
            shutil.rmtree(
                os.path.join(ensemble_path, f"results{npruns*i+j}"),
            )
            os.remove(os.path.join(ensemble_path, f"RESERVOIR{npruns*i+j}.DATA"))
os.remove(os.path.join(ensemble_path, f"TABLES.INC"))
os.remove(os.path.join(ensemble_path, f"CAKE.INC"))


# Create feature tensor.
init_pressures_t: np.ndarray = init_pressures[..., None]  # shape (npoints, 1)
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

init_pressures_v, radii_v = np.meshgrid(
    init_pressures_t.flatten(), radii_t, indexing="ij"
)

features = np.stack(
    [init_pressures_v.flatten(), radii_v.flatten()], axis=-1
)  # ``shape=(npoints * 395, 3)``

# Calculate the well indices from injection rate, cell pressures and bhp.
pressures_t = (
    np.array(pressures)[..., None] * units.BAR_TO_PASCAL
)  # ``shape=(npoints, 400, 1)``, unit: [Pa]

# Get the pressure value of the innermost cell, which equals the bottom hole pressure.
bhp_t: np.ndarray = pressures_t[:, 0]

# Truncate the cell pressures the same way the radii were truncated.
WI_t: np.ndarray = (
    INJECTION_RATE
    * units.Q_per_day_to_Q_per_seconds
    / (bhp_t[..., None] - pressures_t[:, 4:-1])
)  # unit: m*s; ``shape=(npoints, 395, 1)``

# Store the features: pressures, radii, and targets: WI as a dataset.
# Features are in the following order
# 1. initial reservoir pressure [bar]
# 2. cell radius [m]
# Furthermore, first the initial pressures and then the radii (in two nested loops,
# where the pressures are on the lower loop and radii on the higher).
# Targets are
# 1. WI [m*s]
ds = tf.data.Dataset.from_tensor_slices((features, WI_t.flatten()[..., None]))
ds.save(os.path.join(ensemble_path, "pressure_radius_WI"))

# Plot permeability, distance - WI relationship vs Peaceman model

WI = np.vectorize(peaceman_WI)(
    PERMEABILITY * units.MILIDARCY_TO_M2, radii_t, WELL_RADIUS, DENSITY, VISCOSITY
)

features, targets = next(iter(ds.batch(batch_size=len(ds)).as_numpy_iterator()))
features = features.reshape((npoints, 395, 2))[::5, ...]
targets = targets.reshape((npoints, 395, 1))[::5, ...]

for feature, target in zip(features, targets):
    k = feature[0][0]
    plt.scatter(
        feature[..., 1].flatten()[::5],
        target.flatten()[::5],
        label=rf"$p={feature[0][0]}$ Pa",
    )
plt.plot(
    feature[..., 1].flatten()[::5],
    WI[::5],
    label=rf"$p={feature[0][0]}$ Pa Peaceman",
)
plt.legend()
plt.xlabel(r"$r$ [m]")
plt.ylabel(r"$WI$ [ms]")
plt.savefig(os.path.join(dirpath, run_name, "data_vs_Peaceman.png"))
plt.show()


# Three dimensional plot of permeabilities and radii vs. WI, pressure fixed.
fig = plt.figure()
ax = plt.axes(projection="3d")
ax.plot_surface(
    init_pressures_v,
    radii_v,
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
