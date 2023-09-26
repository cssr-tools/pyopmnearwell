import os
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from runspecs import runspecs_ensemble

from pyopmnearwell.ml import ensemble
from pyopmnearwell.utils import formulas, units

dirname: str = os.path.dirname(__file__)

ensemble_dirname: str = os.path.join(dirname, "ensemble")
data_r_e_dirname: str = os.path.join(dirname, "dataset_r_e_pressure")

os.makedirs(ensemble_dirname, exist_ok=True)
os.makedirs(data_r_e_dirname, exist_ok=True)

OPM: str = "/home/peter/Documents/2023_CEMRACS/opm"
FLOW: str = f"{OPM}/build/opm-simulators/bin/flow"
OPM_ML: str = "/home/peter/Documents/2023_CEMRACS/opm_ml"
FLOW_ML: str = f"{OPM_ML}/build/opm-simulators/bin/flow_gaswater_dissolution_diffuse"

# Run ensemble
h2o_ensemble = ensemble.create_ensemble(
    runspecs_ensemble,
)
ensemble.setup_ensemble(
    ensemble_dirname,
    h2o_ensemble,
    os.path.join(dirname, "ensemble.mako"),
    recalc_grid=False,
    recalc_sections=True,
    recalc_tables=False,
)
data: dict[str, Any] = ensemble.run_ensemble(
    FLOW,
    ensemble_dirname,
    runspecs_ensemble,
    ecl_keywords=["PRESSURE"],
    init_keywords=[],
    summary_keywords=[],
    num_report_steps=10,
)

# Get dataset

# Take only every 3rd time step, do not take the initial time step.
features: np.ndarray = np.array(
    ensemble.extract_features(
        data,
        keywords=["PRESSURE"],
        keyword_scalings={"PRESSURE": units.BAR_TO_PASCAL},
    )
)[..., 1::3, :, :]

# The average pressure of the well block will be equal to the pressure at equivalent
# well radius. For a grid block size of 200x200m the equivalent well radius is
# r_e=40.14...m, which is approximately the 160th fine scale cell.
pressures: np.ndarray = features[..., 0].reshape(
    features.shape[0],
    features.shape[1],
    runspecs_ensemble["constants"]["NUM_ZCELLS"],
    -1,
)[
    ..., 160
]  # ``shape = (runspecs_ensemble["npoints"], num_timesteps/3, num_layers)


timesteps: np.ndarray = np.linspace(0, 1, features.shape[-3]) / 1  # unit: [days]

# Calculate WI manually (from the averaged pressures instead of an equivalent well
# radius).
bhps: np.ndarray = features[..., 0].reshape(
    features.shape[0],
    features.shape[1],
    runspecs_ensemble["constants"]["NUM_ZCELLS"],
    -1,
)[
    ..., 0
]  # ``shape = (runspecs_ensemble["npoints"], num_timesteps/3, num_layers)

# We need to divide by num_zcells, as the injection rate is given for the
# entire length of the well. To get the injection rate in one cell we assume the
# injection rate is constant along the well.
injection_rate_per_second_per_cell: float = (
    runspecs_ensemble["constants"]["INJECTION_RATE_PER_SECOND"]
    / runspecs_ensemble["constants"]["NUM_ZCELLS"]
)
WI: np.ndarray = injection_rate_per_second_per_cell / (bhps - pressures)

# Features are, in the following order:
# 1. PRESSURE - cell
# 2. TIME
# shape ``shape = (runspecs_ensemble["npoints"], num_timesteps/3, num_layers, 2)``

ensemble.store_dataset(
    np.stack(
        [
            pressures,
            np.broadcast_to(timesteps[..., None], pressures.shape),
        ],
        axis=-1,
    ),
    WI[..., None],
    data_r_e_dirname,
)

# Comparison vs. Peaceman for the first layer
for pressures_member, bhp_member, target, i in list(
    zip(
        pressures[:: runspecs_ensemble["npoints"], ..., 0],
        bhps[:: runspecs_ensemble["npoints"], ..., 0],
        WI[:: runspecs_ensemble["npoints"], :, 0],
        range(pressures[:: runspecs_ensemble["npoints"], ...].shape[0]),
    )
):
    # Loop through all time steps and collect analytical WIs.
    WI_analytical: list[float] = []
    for pressure in pressures_member:
        # Evaluate density and viscosity.
        density = formulas.co2brinepvt(
            pressure=pressure,
            temperature=runspecs_ensemble["constants"]["INIT_TEMPERATURE"]
            + units.CELSIUS_TO_KELVIN,
            property="density",
            phase="water",
        )

        viscosity = formulas.co2brinepvt(
            pressure=pressure,
            temperature=runspecs_ensemble["constants"]["INIT_TEMPERATURE"]
            + units.CELSIUS_TO_KELVIN,
            property="viscosity",
            phase="water",
        )

        # Calculate the well index from Peaceman. The analytical well index is in [m*s],
        # hence we need to devide by surface density to transform to [m^4*s/kg].
        WI_analytical.append(
            formulas.peaceman_WI(
                k_h=runspecs_ensemble["constants"]["PERMX"]
                * units.MILIDARCY_TO_M2
                * runspecs_ensemble["constants"]["HEIGHT"]
                / runspecs_ensemble["constants"]["NUM_ZCELLS"],
                r_e=formulas.equivalent_well_block_radius(200),
                r_w=0.25,
                rho=density,
                mu=viscosity,
            )
            / runspecs_ensemble["constants"]["SURFACE_DENSITY"]
        )

    # Plot analytical vs. data WI in the upper layer.
    plt.figure()
    plt.scatter(
        timesteps * 3 + 1,
        target,
        label="data",
    )
    plt.plot(
        timesteps * 3 + 1,
        WI_analytical,
        label="Peaceman",
    )
    plt.legend()
    plt.xlabel(r"$t\,[d]$")
    plt.ylabel(r"$WI\,[m^4\cdot s/kg]$")
    plt.savefig(os.path.join(dirname, "ensemble", f"WI_data_vs_Peaceman_{i}.png"))
    plt.show()

    # Plot bhp predicted by Peaceman and data vs actual bhp in the upper layer.
    # NOTE: bhp predicted by data and actual bhp should be identical.
    bhp_data: np.ndarray = injection_rate_per_second_per_cell / target + pressure
    bhp_analytical: np.ndarray = (
        injection_rate_per_second_per_cell / np.array(WI_analytical) + pressure
    )
    plt.figure()
    plt.scatter(
        timesteps * 3 + 1,
        bhp_data,
        label=r"$p_{bh}$ from data $WI$",
    )
    plt.plot(
        timesteps * 3 + 1,
        bhp_analytical,
        label=r"$p_{bh}$ from Peaceman $WI$",
    )
    plt.plot(
        timesteps * 3 + 1,
        bhp_member,
        label=r"actual $p_{bh}$",
    )
    plt.legend()
    plt.xlabel(r"$t\,[d]$")
    plt.ylabel(r"$p\,[Pa]$")
    plt.savefig(os.path.join(dirname, "ensemble", f"pbh_data_vs_Peaceman_{i}.png"))
    plt.show()
