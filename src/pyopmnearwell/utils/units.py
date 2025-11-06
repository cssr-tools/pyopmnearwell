# pylint: skip-file
"""Provide conversions between different units and physical/chemical/... constants."""

from __future__ import annotations

# Permeability
M2_TO_MILIDARCY: float = 1.01324997e15
MILIDARCY_TO_M2: float = 9.869233e-16

# Pressure
PASCAL_TO_BAR: float = 1e-5
BAR_TO_PASCAL: float = 1e5

# Injection rate
Q_per_day_to_Q_per_seconds: float = 1.0 / 86400
Q_per_seconds_to_Q_per_day: float = 86400

# Viscosity
CENTIPOISE_TO_POISE: float = 100
PASCALSECOND_TO_CENTIPOISE: float = 1 / 1000

# Temperature
CELSIUS_TO_KELVIN: float = 273.15
KELVIN_TO_CELSIUS: float = -CELSIUS_TO_KELVIN

# Gravity
GRAVITATIONAL_ACCELERATION: float = 9.8067
"""
Unit: [m/s^2]

Source: https://en.wikipedia.org/wiki/Gravitational_acceleration 

"""

# Boltzmann constant
BOLTZMANN_CONSTANT: float = 1.380649e-23
"""
Unit: [J/K]

Source: https://en.wikipedia.org/wiki/Boltzmann_constant

"""

# Universal gas constant
UNIVERSAL_GAS_CONSTANT: float = 8.31446261815324
"""
Unit: [J/(mol·K)]

Source: https://en.wikipedia.org/wiki/Gas_constant

"""
