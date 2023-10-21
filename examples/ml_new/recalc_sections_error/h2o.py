import os
from typing import Any

from pyopmnearwell.ml import ensemble
from pyopmnearwell.utils import units

dirname: str = os.path.dirname(__file__)
os.makedirs(os.path.join(dirname, "ensemble"), exist_ok=True)
OPM: str = "/home/peter/Documents/2023_CEMRACS/opm"
FLOW: str = f"{OPM}/build/opm-simulators/bin/flow"

# Run ensemble
runspecs_ensemble: dict[str, Any] = {
    "npoints": 1,  # number of ensemble members
    "npruns": 1,  # number of parallel runs
    "variables": {
        "INIT_PRESSURE": (50 * units.BAR_TO_PASCAL, 150 * units.BAR_TO_PASCAL, 300)
    },  # unit: [Pa]
    "constants": {
        "PERMX": 1e-13 * units.M2_TO_MILIDARCY,  # unit: [mD]
        "PERMZ": 1e-13 * units.M2_TO_MILIDARCY,  # unit: [mD]
        "INIT_TEMPERATURE": 40,  # unit: [°C]
        "SURFACE_DENSITY": 998.414,  # unit: [kg/m^3]
        "INJECTION_RATE": 6e1 * 998.414,  # unit: [kg/d]
        "INJECTION_RATE_PER_SECOND": 6e1
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
    recalc_grid=False,
    recalc_sections=False,
    recalc_tables=False,
)
