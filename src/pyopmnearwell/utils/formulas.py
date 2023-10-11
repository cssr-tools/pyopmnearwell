"""Provide useful mathematical formulas for reservoir modelling."""

import math
import os
import subprocess
from typing import Literal


def equivalent_well_block_radius(delta_x: float) -> float:
    """Calculate the equivalent well block radius for a given cell side length.

    Parameters:
        delta_x: _description_

    Returns:
        _description_

    """
    return math.exp(-math.pi / 2) * delta_x


def peaceman_WI(  # pylint: disable=C0103
    k_h: float, r_e: float, r_w: float, rho: float, mu: float
) -> float:
    r"""Compute the well productivity index (adjusted for density and viscosity)
    from the Peaceman well model.

    .. math::
        WI = \frac{2\pi hk\frac{\mu}{\rho}}{\ln(r_e/r_w)}

    Args:
        k_h (float): Permeability times the cell thickness. Unit: [m^3].
        r_e (float): Equivalent well-block radius. Needs to have the same unit as ``r_w``.
        r_w (float): Wellbore radius. Needs to have the same unit as ``r_e``.
        rho (float): Density. Unit: [kg/m^3].
        mu (float): Viscosity. Unit: [Pa*s].

    Returns:
        WI (float): :math:`WI`. Unit: [m*s].

    """
    WI = (2 * math.pi * k_h) / (math.log(r_e / r_w))
    return WI * rho / mu


def two_phase_peaceman_WI(  # pylint: disable=C0103
    k_h: float,
    r_e: float,
    r_w: float,
    rho_1: float,
    mu_1: float,
    k_r1: float,
    rho_2: float,
    mu_2: float,
    k_r2: float,
) -> float:
    r"""Compute the well productivity index (adjusted for density, viscosity and
    relative permeabilties) from the Ptwo-phase eaceman well model.

    Cf. [A. Yapparova, B. Lamy-Chappuis, S. W. Scott, and T. Driesner, “A Peaceman-type
    well model for the 3D Control Volume Finite Element Method and numerical simulations
    of supercritical geothermal resource utilization” 2022,
    doi: 10.1016/j.geothermics.2022.102516.]


    .. math::
        WI = \frac{2\pi h\mathbf{k}}{\ln(r_e/r_w)}\left(\frac{k_{r,1}}{\mu_1} +
        \frac{k_{r,2}}{\mu_2})


    Note:
        The result is only accurate for fine grid sizes.


    Args:
        k_h (float): Permeability times the cell thickness (thickness fix to 1 m). Unit: [m^3].
        r_e (float): Equivalent well-block radius. Needs to have the same unit as ``r_w``.
        r_w (float): Wellbore radius. Needs to have the same unit as ``r_e``.
        rho_1 (float): Density of phase 1. Unit: [kg/m^3].
        mu_1 (float): Viscosity of phase 1. Unit: [Pa*s].
        k_r1 (float): Relative permeability of phase 1.
        rho_2 (float): Density of phase 2. Unit: [kg/m^3].
        mu_2 (float): Viscosity of phase 2. Unit: [Pa*s].
        k_r2 (float): Relative permeability of phase 2.

    Returns:
        WI (float): :math:`WI`. Unit: [m*s].

    """
    total_mobility: float = (k_r1 * rho_1) / mu_1 + (k_r2 * rho_2) / mu_2
    WI = (2 * math.pi * k_h) / (math.log(r_e / r_w))
    return WI * total_mobility


def data_WI(q: float, p_w: float, p_gb: float) -> float:  # pylint: disable=C0103
    r"""Compute the well productivity index from given data.

    .. math::
        WI = \frac{q}{p_w - p_{gb}

    Args:
        q (float): Injection rate. Unit: [m^3/s].
        p_w (float): Bottom hole pressure. Unit: [Pa].
        p_gb (float): Grid block pressure. Unit: [Pa].

    Returns:
        WI (float): :math:`WI`. Unit: [m^4*s/kg].

    """
    WI = q / (p_w - p_gb)
    return WI


def co2brinepvt(
    pressure: float,
    temperature: float,
    property: Literal["density", "viscosity"],
    phase: Literal["CO2", "water"],
) -> float:
    """Call OPM's ``co2brinepvt`` to calculate density/viscosity.

    Args:
        pressure (float): Unit: [Pa].
        temperature (float): Unit: [K].
        property (Literal["density", "viscosity"]): Returned phase property. Density in
        [kg/m^3], viscosity in [].
        phase (Literal["CO2", "water"]): Phase of interest.

    Returns:
        quantity (float): Density (unit: [kg/m^3]) or viscosity (unit: [Pa*s])

    """
    OPM_ML: str = "/home/peter/Documents/2023_CEMRACS/opm_ml"
    CO2BRINEPVT: str = os.path.join(OPM_ML, "build/opm-common/bin/co2brinepvt")
    with subprocess.Popen(
        [
            CO2BRINEPVT,
            property,
            phase if phase == "CO2" else "brine",
            str(pressure),
            str(temperature),
        ],
        stdout=subprocess.PIPE,
    ) as proc:
        # Ignore mypy complaining.
        value = float(proc.stdout.read())  # type: ignore
    return value
