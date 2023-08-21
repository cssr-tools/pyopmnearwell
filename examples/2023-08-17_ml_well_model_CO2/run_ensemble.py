""""Run nearwell CO2 storage simulations in OPM-Flow for an ensemble of varying initial
initial pressures and construct a dataset containing cell pressures, time since
injection and cell center radii as features and well indices as targets.

Features:
    1. pressure [Pa]: Measured each report step at the cell centers.
    2. time [h]: Time since beginning of simulation at report step.
    3. radius [m]: Cell center radii.

Targets:
    1. WI [[m^4*s/kg]]: Calculated at the given radius.

Note: The wellbore radius, permeability, density and viscosity are fixed.


"""
from __future__ import annotations

import datetime
import logging
import math
import os
import shutil
import subprocess

import matplotlib.pyplot as plt
import numpy as np
import runspecs
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


# Path to OPM with ml and co2brinepvt.
OPM_ML: str = "/home/peter/Documents/2023_CEMRACS/opm_ml"
CO2BRINEPVT: str = f"{OPM_ML}/build/opm-common/bin/co2brinepvt"

shutil.copyfile(
    os.path.join(dirpath, "TABLES.INC"),
    os.path.join(dirpath, run_name, "TABLES.INC"),
)
shutil.copyfile(
    os.path.join(dirpath, "CAKE.INC"),
    os.path.join(dirpath, run_name, "CAKE.INC"),
)

# Create pressure ensemble.

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
for i, pressure in enumerate(runspecs.INIT_PRESSURES):
    var = {
        "permeability_x": runspecs.PERMEABILITY,
        "init_pressure": pressure,
        "temperature": runspecs.TEMPERATURE,
        "injection_rate": runspecs.INJECTION_RATE,
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
for i in range(round(runspecs.NPOINTS / runspecs.NPRUNS)):
    os.system(
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{runspecs.NPRUNS*i}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{runspecs.NPRUNS*i}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{runspecs.NPRUNS*i+1}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{runspecs.NPRUNS*i+1}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{runspecs.NPRUNS*i+2}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{runspecs.NPRUNS*i+2}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{runspecs.NPRUNS*i+3}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{runspecs.NPRUNS*i+3}')} {FLAGS} & "
        f"{FLOW}"
        + f" {os.path.join(ensemble_path, f'RESERVOIR{runspecs.NPRUNS*i+4}.DATA')}"
        + f" --output-dir={os.path.join(ensemble_path, f'results{runspecs.NPRUNS*i+4}')} {FLAGS} & wait"
    )
    for j in range(runspecs.NPRUNS):
        with open_ecl_file(
            os.path.join(
                ensemble_path,
                f"results{runspecs.NPRUNS*i+j}",
                f"RESERVOIR{runspecs.NPRUNS*i+j}.UNRST",
            )
        ) as ecl_file:
            # Each pressure array has shape ``[number_report_steps, number_cells]``
            # Truncate the first report step at starting time. Take only every third
            # time step.
            pressures.append(np.array(ecl_file.iget_kw("PRESSURE"))[1::3])
            # We assume constant report step delta. The steps cannot be taken directly
            # from the ecl file, as the hours and minutes are missing.
            # Truncate the starting time.
            if i == 0 and j == 0:
                report_times: np.ndarray = np.linspace(
                    0,
                    (
                        ecl_file.report_dates[-1] - datetime.datetime(2000, 1, 1, 0, 0)
                    ).total_seconds()
                    / 3600,
                    ecl_file.num_report_steps(),
                )[1::3]
        # Remove the run files and result folder (except for the first one).
        if runspecs.NPRUNS * i + j > 0:
            shutil.rmtree(
                os.path.join(ensemble_path, f"results{runspecs.NPRUNS*i+j}"),
            )
            os.remove(
                os.path.join(ensemble_path, f"RESERVOIR{runspecs.NPRUNS*i+j}.DATA")
            )
os.remove(os.path.join(ensemble_path, f"TABLES.INC"))
os.remove(os.path.join(ensemble_path, f"CAKE.INC"))


# Create feature tensor.
pressures_t = (
    np.array(pressures) * units.BAR_TO_PASCAL
)  # ``shape=(runspecs.NPOINTS, num_report_steps, 400)``, unit: [Pa]

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

report_times_v, radii_v = np.meshgrid(report_times, radii_t, indexing="ij")

features = np.stack(
    [
        pressures_t[..., 4:-1].flatten(),
        np.tile(report_times_v.flatten(), runspecs.NPOINTS),
        np.tile(radii_v.flatten(), runspecs.NPOINTS),
    ],
    axis=-1,
)  # ``shape=(runspecs.NPOINTS * num_report_steps * 395, 2)``

# Calculate the well indices from injection rate, cell pressures and bhp.
# Get the pressure value of the innermost cell, which equals the bottom hole pressure.
# Ignore the first report step, as it has constant pressure in the interval
bhp_t: np.ndarray = pressures_t[..., 0]

# Truncate the cell pressures the same way the radii were truncated.
# Multiply by 6 to account for the 6 times higher injection rate of a 360° well.
WI_data: np.ndarray = (
    runspecs.INJECTION_RATE
    * units.Q_per_day_to_Q_per_seconds
    / (bhp_t[..., None] - pressures_t[..., 4:-1])
) * 6  # unit: m^4*s/kg; ``shape=(runspecs.NPOINTS, num_report_steps, 395, 1)``
a = list(zip(features[:5, -1, ...], WI_data[:5, -1, ...]))

ds = tf.data.Dataset.from_tensor_slices((features, WI_data.flatten()[..., None]))
ds.save(os.path.join(ensemble_path, "pressure_radius_WI"))

# Plot pressure, distance - WI relationship vs Peaceman model

features = np.reshape(features, (runspecs.NPOINTS, -1, 395, 3))


proc = subprocess.Popen(["cat", "/etc/services"], stdout=subprocess.PIPE, shell=True)
# Fix the last time step
for feature, target in list(zip(features[:5, -1, ...], WI_data[:5, -1, ...])):
    # Evalute density and viscosity
    pressure: float = feature[75][0]
    with subprocess.Popen(
        [
            CO2BRINEPVT,
            "density",
            "CO2",
            str(pressure),
            str(runspecs.TEMPERATURE + units.CELSIUS_TO_KELVIN),
        ],
        stdout=subprocess.PIPE,
    ) as proc:
        density = float(proc.stdout.read())
    with subprocess.Popen(
        [
            CO2BRINEPVT,
            "viscosity",
            "CO2",
            str(pressure),
            str(runspecs.TEMPERATURE + units.CELSIUS_TO_KELVIN),
        ],
        stdout=subprocess.PIPE,
    ) as proc:
        viscosity = float(proc.stdout.read())
    logger.info(f"p: {pressure} rho: {density} mu: {viscosity}")
    logger.info(
        f"WI: {peaceman_WI( runspecs.PERMEABILITY * units.MILIDARCY_TO_M2,radii_t[0],runspecs.WELL_RADIUS,density,viscosity)}"
    )

    # Compute total mobility
    VISCOSITY_W = 0.00065
    RELPERM_W = 0.6
    RELPERM_G = 0.05
    lambda_t = (
        runspecs.PERMEABILITY
        * units.MILIDARCY_TO_M2
        * (RELPERM_G / viscosity + RELPERM_W / VISCOSITY_W)
    )
    logger.info(
        f"lambda_t * mu_g/ k : {viscosity * (RELPERM_G / viscosity + RELPERM_W / VISCOSITY_W)}"
    )
    WI_analytical = (
        np.vectorize(peaceman_WI)(
            lambda_t,
            radii_t,
            runspecs.WELL_RADIUS,
            density,
            1,
        )
        / runspecs.SURFACE_DENSITY
    )
    plt.figure()
    plt.scatter(
        radii_t[::5],
        target[::5],
        label="data",
    )
    plt.plot(
        radii_t,
        WI_analytical,
        label="Peaceman",
    )
    plt.legend()
    plt.title(
        rf"$p={feature[75][0]:.3e}\,[Pa]$ at $r={feature[75][2]:.2f}\,[m]$ $t={feature[0][1]:2f}\,[h]$\\n"
        + rf"Peaceman evaluated at p={feature[75][0]:.3e}"
    )
    plt.xlabel(r"$r\,[m]$")
    plt.ylabel(r"$WI\,[m^4\cdot s/kg]$")
    plt.savefig(
        os.path.join(dirpath, run_name, f"data_vs_Peaceman_p_{feature[-1][0]:.3e}.png")
    )
    plt.show()


# Three dimensional plot of pressure and radii vs. WI. Data taken at the last time step
plt.figure()
ax = plt.axes(projection="3d")
ax.plot_surface(
    features[:, -1, :, 0],
    features[:, -1, :, 2],
    np.squeeze(WI_data[:, -1, :]),
    rstride=1,
    cstride=1,
    cmap="viridis",
    edgecolor="none",
)
ax.set_xlabel(r"$p\,[Pa]$")
ax.set_ylabel(r"$r\,[m]$")
ax.set_title(rf"$WI\,[m^4*s/kg]$ at $t={features[0][-1][0][0]:.2f}")
plt.savefig(os.path.join(dirpath, run_name, "data_3d.png"))
plt.show()
