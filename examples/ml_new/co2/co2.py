import os
from typing import Any

import numpy as np

from pyopmnearwell.ml import ensemble, integration, nn
from pyopmnearwell.utils import units

dirname: str = os.path.dirname(__file__)
os.makedirs(os.path.join(dirname, "ensemble"), exist_ok=True)
os.makedirs(os.path.join(dirname, "dataset"), exist_ok=True)
os.makedirs(os.path.join(dirname, "nn"), exist_ok=True)
os.makedirs(os.path.join(dirname, "integration"), exist_ok=True)
OPM: str = "/home/peter/Documents/2023_CEMRACS/opm"
FLOW: str = f"{OPM}/build/opm-simulators/bin/flow"
OPM_ML: str = "/home/peter/Documents/2023_CEMRACS/opm_ml"
FLOW_ML: str = f"{OPM_ML}/build/opm-simulators/bin/flow_gaswater_dissolution_diffuse"

# Run ensemble
# Create permeability fields:

num_layers: int = 5
height: float = 20.0

variables: dict[str, tuple[float, float, int]] = {
    f"PERMX_{i}": (  # unit: [mD]
        1e-15 * units.M2_TO_MILIDARCY,
        1e-9 * units.M2_TO_MILIDARCY,
        40,
    )
    for i in range(num_layers)
}

# Vertical permeabilties correspond to horizontal permeability.
variables.update(
    {
        f"PERMZ_by_{key}": (  # unit: [mD]
            1,
            1,
            npoints,
        )
        for key, (_, __, npoints) in variables.items()
    }
)

variables.update(
    {
        "INIT_PRESSURE": (
            50 * units.BAR_TO_PASCAL,
            80 * units.BAR_TO_PASCAL,
            30,
        ),  # unit: [Pa]
        "INIT_TEMPERATURE": (20, 40, 20),  # unit: [°C])
    }
)

runspecs_ensemble: dict[str, Any] = {
    "npoints": 5,  # number of ensemble members
    "npruns": 5,  # number of parallel runs
    "variables": variables,
    "constants": {
        "SURFACE_DENSITY": 1.86843,  # unit: [kg/m^3]
        "INJECTION_RATE": 1e5 * 1.86843,  # unit: [kg/d]
        "INJECTION_RATE_PER_SECOND": 1e5
        * units.Q_per_day_to_Q_per_seconds,  # unit: [m^3/s]
        "WELL_RADIUS": 0.25,  # unit: [m]; Fixed during training.
        "FLOW": FLOW,
        "NUM_LAYERS": num_layers,
        "HEIGHT": height,
        "THICKNESS": height / num_layers,
    },
}

co2_ensemble = ensemble.create_ensemble(
    runspecs_ensemble,
    efficient_sampling=[f"PERMX_{i}" for i in range(num_layers)]
    + [f"PERMZ_by_PERMX_{i}" for i in range(num_layers)],
)
ensemble.setup_ensemble(
    os.path.join(dirname, "ensemble"),
    co2_ensemble,
    os.path.join(dirname, "co2_ensemble.mako"),
    recalc_grid=False,
    recalc_sections=True,
    recalc_tables=False,
)
data: dict[str, Any] = ensemble.run_ensemble(
    FLOW,
    os.path.join(dirname, "ensemble"),
    runspecs_ensemble,
    ecl_keywords=["PRESSURE", "SGAS"],
    init_keywords=["PERMX", "PERMZ"],
    summary_keywords=[],
)


# Get dataset
# Get only data from the cells at 25 m distance from the well. Take only every 3rd time step.
features: np.ndarray = np.array(
    ensemble.extract_features(
        data,
        keywords=["PRESSURE", "SGAS", "PERMX", "PERMZ"],
        keyword_scalings={"PRESSURE": units.BAR_TO_PASCAL},
    )
)[..., ::3, 100::400, :]

timesteps: np.ndarray = np.arange(features.shape[-3])  # No unit.

WI: np.ndarray = ensemble.calculate_WI(data, runspecs_ensemble, num_zcells=num_layers)[
    ..., ::3, 100::400
]

# Features are, in the following order:
# 1. PRESSURE
# 2. SGAS
# 3. PERMX
# 4. PERMZ
# 5. TIME
ensemble.store_dataset(
    np.stack(
        [
            features[..., 0].flatten(),
            features[..., 1].flatten(),
            features[..., 2].flatten(),
            features[..., 3].flatten(),
            np.broadcast_to(timesteps[..., None], features[..., 0].shape).flatten(),
        ],
        axis=-1,
    ),
    WI.flatten()[..., None],
    os.path.join(dirname, "dataset"),
)

# Train model
# model = nn.get_FCNN(ninputs=5, noutputs=1)
# train_data, val_data = nn.scale_and_prepare_dataset(
#     os.path.join(dirname, "dataset"),
#     feature_names=["pressure", "radius"],
#     savepath=os.path.join(dirname, "nn"),
# )
# nn.train(model, train_data, val_data, savepath=os.path.join(dirname, "nn"), epochs=500)

# # Integrate
# runspecs_integration: dict[str, Any] = {
#     "variables": {
#         "GRID_SIZE": [20, 20, 100],
#         "ML_MODEL_PATH": [os.path.join(dirname, "nn", "WI.model"), "", ""],
#         "RUN_NAME": ["125x125m_NN", "125x125m_Peaceman", "25x25m_Peaceman"],
#     },
#     "constants": {
#         "PERMX": 1e-13 * units.M2_TO_MILIDARCY,  # unit: [mD]
#         "PERMZ": 1e-13 * units.M2_TO_MILIDARCY,  # unit: [mD]
#         "INIT_PRESSURE": (50 + 80) / 2 * units.BAR_TO_PASCAL,  # unit: [Pa]
#         "INIT_TEMPERATURE": 40,  # unit: [°C]
#         "SURFACE_DENSITY": 998.414,  # unit: [kg/m^3]
#         "INJECTION_RATE": 1e1 * 998.414,  # unit: [kg/d]
#         "INJECTION_RATE_PER_SECOND": 1e1
#         * 998.414
#         * units.Q_per_day_to_Q_per_seconds,  # unit: [kg/s]
#         "WELL_RADIUS": 0.25,  # unit: [m]; Fixed during training.
#         "RESERVOIR_SIZE": 5000,  # unit: [m]
#         "FLOW": FLOW_ML,
#     },
# }
# integration.recompile_flow(
#     os.path.join(dirname, "nn", "scales.csv"), "h2o_2_inputs", OPM_ML
# )
# integration.run_integration(
#     runspecs_integration,
#     os.path.join(dirname, "integration"),
#     os.path.join(dirname, "h2o_integration.mako"),
# )
