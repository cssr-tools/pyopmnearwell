"""Provide some common conversions between different units."""

# Permeability
M2_TO_MILIDARCY: float = 1.01324997e15
MILIDARCY_TO_M2: float = 9.869233e-16

# Pressure
PASCAL_TO_BAR: float = 1.0e-5
BAR_TO_PASCAL: float = 1e5

# Injection rate
Q_per_day_to_Q_per_seconds: float = 1.0 / 86400
Q_per_seconds_to_Q_per_day: float = 86400

# Viscosity
CENTIPOISE_TO_POISE: float = 100
PASCALSECOND_TO_CENTIPOISE: float = 1 / 1000
