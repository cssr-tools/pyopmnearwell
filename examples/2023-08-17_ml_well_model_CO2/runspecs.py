import math

import numpy as np

import pyopmnearwell.utils.units as units

# Matrix and fluid properties
PERMEABILITY: float = 1e-12 * units.M2_TO_MILIDARCY  # unit: mD
TEMPERATURE: float = 25  # unit: °C
INJECTION_RATE: float = 5.352087e3  # unit: [m^3/d]

X: float = 2.500000e-01  # Outer coordinates of first cell.
Y: float = -1.443376e-01
WELL_RADIUS: float = math.sqrt(X**2 + Y**2)  # unit: [m]; Fixed during training.
RESERVOIR_SIZE: float = 5000  # unit: m;

SURFACE_DENSITY: float = 1.86843
DENSITY: float = 172.605  # unit: kg/m^3; for 57.5 bar, 25 °C.
VISCOSITY: float = 1.77645e-05  # unit: Pa*s; for 57.5 bar, 25 °C

# Ensemble specs
NPOINTS: int = 5  # number of ensemble members
NPRUNS: int = 5  # number of parallel runs
INIT_PRESSURE_MAX: float = 80
INIT_PRESSURE_MIN: float = 50
INIT_PRESSURES: np.ndarray = np.random.uniform(
    INIT_PRESSURE_MIN, INIT_PRESSURE_MAX, NPOINTS
)  # unit: bar
