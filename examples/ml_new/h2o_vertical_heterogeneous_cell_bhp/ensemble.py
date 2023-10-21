import os
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from runspecs import runspecs_ensemble_3 as runspecs_ensemble

from pyopmnearwell.ml import ensemble
from pyopmnearwell.utils import formulas, units

dirname: str = os.path.dirname(__file__)

ensemble_dirname: str = os.path.join(dirname, runspecs_ensemble["name"])
data_r_e_dirname: str = os.path.join(dirname, f"dataset_{runspecs_ensemble['name']}")

os.makedirs(ensemble_dirname, exist_ok=True)
os.makedirs(data_r_e_dirname, exist_ok=True)

# Run ensemble
h2o_ensemble = ensemble.create_ensemble(
    runspecs_ensemble,
    efficient_sampling=[
        f"PERM_{i}" for i in range(runspecs_ensemble["constants"]["NUM_ZCELLS"])
    ],
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
    runspecs_ensemble["constants"]["FLOW"],
    ensemble_dirname,
    runspecs_ensemble,
    ecl_keywords=["PRESSURE", "FLOWATI+"],
    init_keywords=["PERMX"],
    summary_keywords=[],
    num_report_steps=10,
)

# Get dataset

# Take only every 3rd time step.
features: np.ndarray = np.array(
    ensemble.extract_features(
        data,
        keywords=["PRESSURE", "PERMX", "FLOWATI+"],
        keyword_scalings={
            "PRESSURE": units.BAR_TO_PASCAL,
        },
    )
)[..., ::3, :, :]

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
]  # ``shape = (runspecs_ensemble["npoints"], num_timesteps/3, num_layers); unit [Pa]

# The permeabilities are equal for an entire layer. -> Take the first cell value
permeabilities: np.ndarray = features[..., 1].reshape(
    features.shape[0],
    features.shape[1],
    runspecs_ensemble["constants"]["NUM_ZCELLS"],
    -1,
)[
    ..., 0
]  # ``shape = (runspecs_ensemble["npoints"], num_timesteps/3, num_layers); unit [mD]

timesteps: np.ndarray = np.linspace(0, 1, features.shape[-3]) / 1  # unit: [day]

# Calculate WI manually.

# Take the pressure values of the well blocks as bhp.
bhps: np.ndarray = features[..., 0].reshape(
    features.shape[0],
    features.shape[1],
    runspecs_ensemble["constants"]["NUM_ZCELLS"],
    -1,
)[..., 0]


# Get the individual injection rates per second for each cell. Multiply by 6 to account
# for the 60° cake and transform to rate per second.
injection_rate_per_second_per_cell: np.ndarray = (
    features[..., 2].reshape(
        features.shape[0],
        features.shape[1],
        runspecs_ensemble["constants"]["NUM_ZCELLS"],
        -1,
    )[..., 0]
    * 6
    * units.Q_per_day_to_Q_per_seconds
)  # ``shape = (runspecs_ensemble["npoints"], num_timesteps/3, num_layers)

WI: np.ndarray = injection_rate_per_second_per_cell / (bhps - pressures)

# Features are, in the following order:
# 1. PRESSURE - cell; unit [Pa]
# 2. PERMEABILITY - cell; unit [mD]
# 3. TIME; unit [day]
# shape ``shape = (runspecs_ensemble["npoints"], num_timesteps/3, num_layers, 3)``

ensemble.store_dataset(
    np.stack(
        [
            pressures,
            permeabilities,
            np.broadcast_to(timesteps[..., None], pressures.shape),
        ],
        axis=-1,
    ),
    WI[..., None],
    data_r_e_dirname,
)

# Comparison vs. Peaceman for the first, fifth and last layer. Only first ensemble
# member.
for i in [0, 5, 9]:
    pressures_member = pressures[0, ..., i]
    bhp_member = bhps[0, ..., i]
    permeability_member = permeabilities[0, ..., i]
    injection_rate_per_second_per_cell_member = injection_rate_per_second_per_cell[
        0, ..., i
    ]
    target = WI[0, ..., i]
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
                k_h=permeability_member[0]  # Permeability is equal for all time steps,
                # just get the first one.
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
        timesteps,
        target,
        label="data",
    )
    plt.plot(
        timesteps,
        WI_analytical,
        label="Peaceman",
    )
    plt.legend()
    plt.xlabel(r"$t\,[d]$")
    plt.ylabel(r"$WI\,[m^4\cdot s/kg]$")
    plt.title(f"Layer {i}")
    plt.savefig(os.path.join(ensemble_dirname, f"WI_data_vs_Peaceman_{i}.png"))
    plt.show()

    # Plot bhp predicted by Peaceman and data vs actual bhp in the upper layer.
    # NOTE: bhp predicted by data and actual bhp should be identical.
    bhp_data: np.ndarray = (
        injection_rate_per_second_per_cell_member / target + pressures_member
    )
    bhp_analytical: np.ndarray = (
        injection_rate_per_second_per_cell_member / np.array(WI_analytical)
        + pressures_member
    )
    plt.figure()
    plt.scatter(
        timesteps,
        bhp_data,
        label=r"$p_{bh}$ from data $WI$",
    )
    plt.plot(
        timesteps,
        bhp_analytical,
        label=r"$p_{bh}$ from Peaceman $WI$",
    )
    plt.plot(
        timesteps,
        bhp_member,
        label=r"actual $p_{bh}$",
    )
    plt.legend()
    plt.xlabel(r"$t\,[d]$")
    plt.ylabel(r"$p\,[Pa]$")
    plt.title(f"Layer {i}")
    plt.savefig(os.path.join(ensemble_dirname, f"pbh_data_vs_Peaceman_{i}.png"))
    plt.show()
