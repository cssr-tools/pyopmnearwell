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
runspecs_ensemble: dict[str, Any] = {
    "npoints": 5,  # number of ensemble members
    "npruns": 5,  # number of parallel runs
    "variables": {
        "INIT_PRESSURE": (50 * units.BAR_TO_PASCAL, 80 * units.BAR_TO_PASCAL, 5)
    },  # unit: [Pa]
    "constants": {
        "PERMX": 1e-13 * units.M2_TO_MILIDARCY,  # unit: [mD]
        "PERMZ": 1e-13 * units.M2_TO_MILIDARCY,  # unit: [mD]
        "INIT_TEMPERATURE": 40,  # unit: [°C]
        "SURFACE_DENSITY": 998.414,  # unit: [kg/m^3
        "INJECTION_RATE": 1e1 * 998.414,  # unit: [kg/d]
        "INJECTION_RATE_PER_SECOND": 1e1
        * 998.414
        * units.Q_per_day_to_Q_per_seconds,  # unit: [kg/s]
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
    ..., -1, 4:-4
]
radiis: np.ndarray = ensemble.calculate_radii(
    os.path.join(dirname, "ensemble", "preprocessing", "GRID.INC")
)
WI: np.ndarray = ensemble.calculate_WI(data, runspecs_ensemble)[..., -1, 4:-4]
ensemble.store_dataset(
    np.stack([pressures, radiis]).reshape((-1, 2)),
    WI.flatten()[..., None],
    os.path.join(dirname, "ensemble"),
)

# Train model
model = nn.get_FCNN(ninputs=2, noutputs=1)
train_data, val_data = nn.scale_and_prepare_dataset(
    os.path.join(dirname, "dataset", ""),
    feature_names=["pressure", "radius"],
    savepath=os.path.join(dirname, "nn"),
)
nn.train(
    model,
    train_data,
    val_data,
    savepath=os.path.join(dirname, "nn"),
)

# Integrate
runspecs_integration: dict[str, Any] = {
    "variables": {
        "GRID_SIZE": [20, 100],
        "ML_MODEL_PATH": [os.path.join(dirname, "nn", "WI.model"), "", ""],
        "RUN_NAME": ["125x125m NN", "125x125m Peaceman", "25x25m Peaceman"],
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
integration.recompile_flow(os.path.join(dirname, "nn", "scales.csv"), OPM_ML)
integration.run_integration(
    runspecs_integration,
    os.path.join(dirname, "integration"),
    os.path.join(dirname, "h2o_integration.mako"),
)
