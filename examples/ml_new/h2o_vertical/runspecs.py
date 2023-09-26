import copy
from typing import Any

from pyopmnearwell.utils import formulas, units

OPM: str = "/home/peter/Documents/2023_CEMRACS/opm_ml"
FLOW: str = f"{OPM}/build/opm-simulators/bin/flow_gaswater_dissolution_diffuse"

npoints: int = 100
injection_rate: float = 5e3  # unit: [m^3/d]
surface_density: float = 998.414  # unit: [kg/m^3]

variables: dict[str, tuple[float, float, int]] = {
    "INIT_PRESSURE": (
        50 * units.BAR_TO_PASCAL,
        130 * units.BAR_TO_PASCAL,
        npoints,
    ),  # unit: [Pa]
}

constants: dict[str, Any] = {
    "PERMX": 1e-12 * units.M2_TO_MILIDARCY,  # unit: [mD]
    "PERMZ": 1e-12 * units.M2_TO_MILIDARCY,  # unit: [mD]
    "INIT_TEMPERATURE": 25,  # unit: [°C])
    "SURFACE_DENSITY": surface_density,  # unit: [kg/m^3]
    "INJECTION_RATE": injection_rate * surface_density,  # unit: [kg/d]
    "INJECTION_RATE_PER_SECOND": injection_rate
    * units.Q_per_day_to_Q_per_seconds,  # unit: [m^3/s]
    # NOTE: 1e4 m^3/day is approx 200L/s for each meter of well. Setting this higher
    # (e.g., 6e4 m^3/day) will result in inaccurate results as the PVT values are
    # exceeded.
    "WELL_RADIUS": 0.25,  # unit: [m]; Fixed during training.
    "NUM_ZCELLS": 10,
    "HEIGHT": 50,
    "FLOW": FLOW,
    "OPM": OPM,
}


runspecs_ensemble: dict[str, Any] = {
    "npoints": npoints,  # number of ensemble members
    "npruns": min(npoints, 5),  # number of parallel runs
    "variables": variables,
    "constants": constants,
}


constants_integration: dict[str, Any] = copy.deepcopy(constants)
constants_integration.update(
    {
        "INIT_PRESSURE": 55 * units.BAR_TO_PASCAL,  # unit: [Pa]
        "RESERVOIR_SIZE": 5000,  # unit: [m]
    }
)

runspecs_integration: dict[str, Any] = {
    "variables": {
        "GRID_SIZE": [20, 20, 100],
        "RUN_NAME": ["125x125m_NN", "125x125m_Peaceman", "25x25m_Peaceman"],
    },
    "constants": constants_integration,
}
