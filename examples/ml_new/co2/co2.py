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


runspecs_ensemble: dict[str, Any] = {
    "npoints": 300,  # number of ensemble members
    "npruns": 5,  # number of parallel runs
    "variables": {
        "INIT_PRESSURE": (
            50 * units.BAR_TO_PASCAL,
            80 * units.BAR_TO_PASCAL,
            300,
        ),  # unit: [Pa]
        "INIT_TEMPERATURE": (20, 40, 300),  # unit: [°C]
    },
    "constants": {
        "PERMX": 1e-13 * units.M2_TO_MILIDARCY,  # unit: [mD]
        "PERMZ": 1e-13 * units.M2_TO_MILIDARCY,  # unit: [mD]
        "SURFACE_DENSITY": 1.86843,  # unit: [kg/m^3]
        "INJECTION_RATE": 1e3 * 1.86843,  # unit: [kg/d]
        "INJECTION_RATE_PER_SECOND": 1e3
        * units.Q_per_day_to_Q_per_seconds,  # unit: [m^3/s]
        "WELL_RADIUS": 0.25,  # unit: [m]; Fixed during training.
        "FLOW": FLOW,
    },
}

h2o_ensemble = ensemble.create_ensemble(runspecs_ensemble)
ensemble.setup_ensemble(
    os.path.join(dirname, "ensemble"),
    h2o_ensemble,
    os.path.join(dirname, "h2o_ensemble.mako"),
)
data: dict[str, Any] = ensemble.run_ensemble(
    FLOW, os.path.join(dirname, "ensemble"), runspecs_ensemble, ["PRESSURE"], []
)


# Get dataset
# Truncate outer and inner cells. Truncate every time step but the last one.
pressures: np.ndarray = ensemble.extract_features(data, keywords=["PRESSURE"])[
    ..., -1, 4:-4, :
]
# The innermost radius corresponds to the bottom hole pressure and is already truncated
# for the ``pressures`` and ``WI`` arrays.
radiis: np.ndarray = ensemble.calculate_radii(
    os.path.join(dirname, "ensemble", "preprocessing", "GRID.INC")
)[5:-4]
assert pressures.shape[-2] == radiis.shape[-1]
WI: np.ndarray = ensemble.calculate_WI(data, runspecs_ensemble)[..., -1, 4:-4]
ensemble.store_dataset(
    np.stack(
        [
            pressures.flatten(),
            np.tile(radiis, np.prod(pressures.shape[:-2]).item()),
        ],
        axis=-1,
    ),
    WI.flatten()[..., None],
    os.path.join(dirname, "dataset"),
)

# Train model
model = nn.get_FCNN(ninputs=2, noutputs=1)
train_data, val_data = nn.scale_and_prepare_dataset(
    os.path.join(dirname, "dataset"),
    feature_names=["pressure", "radius"],
    savepath=os.path.join(dirname, "nn"),
)
nn.train(model, train_data, val_data, savepath=os.path.join(dirname, "nn"), epochs=500)

# Integrate
runspecs_integration: dict[str, Any] = {
    "variables": {
        "GRID_SIZE": [20, 20, 100],
        "ML_MODEL_PATH": [os.path.join(dirname, "nn", "WI.model"), "", ""],
        "RUN_NAME": ["125x125m_NN", "125x125m_Peaceman", "25x25m_Peaceman"],
    },
    "constants": {
        "PERMX": 1e-13 * units.M2_TO_MILIDARCY,  # unit: [mD]
        "PERMZ": 1e-13 * units.M2_TO_MILIDARCY,  # unit: [mD]
        "INIT_PRESSURE": (50 + 80) / 2 * units.BAR_TO_PASCAL,  # unit: [Pa]
        "INIT_TEMPERATURE": 40,  # unit: [°C]
        "SURFACE_DENSITY": 998.414,  # unit: [kg/m^3]
        "INJECTION_RATE": 1e1 * 998.414,  # unit: [kg/d]
        "INJECTION_RATE_PER_SECOND": 1e1
        * 998.414
        * units.Q_per_day_to_Q_per_seconds,  # unit: [kg/s]
        "WELL_RADIUS": 0.25,  # unit: [m]; Fixed during training.
        "RESERVOIR_SIZE": 5000,  # unit: [m]
        "FLOW": FLOW_ML,
    },
}
integration.recompile_flow(
    os.path.join(dirname, "nn", "scales.csv"), "h2o_2_inputs", OPM_ML
)
integration.run_integration(
    runspecs_integration,
    os.path.join(dirname, "integration"),
    os.path.join(dirname, "h2o_integration.mako"),
)
