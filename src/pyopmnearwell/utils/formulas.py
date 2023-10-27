# pylint: skip-file
"""Provide useful mathematical formulas for reservoir modelling."""

import math
import os
import pathlib
import subprocess
from typing import Literal

import numpy as np
from numpy.typing import ArrayLike

from pyopmnearwell.utils import units

# TODO: Change the typing to typevars. There needs to be some logic, e.g., in case some
# of the inputs are floats and some are arrays.
# NOTE: The output type ``ArrayLike`` is way too broad.

R_E_RATIO: float = math.exp(-math.pi / 2)


def pyopmnearwell_correction(theta: ArrayLike = math.pi / 3) -> ArrayLike:
    r"""Calculate a correction factor that scales cell volume, equivalent radius etc.
    from a 2D triangle grid to a radial grid.

    In pyopmnearwell, when using the `cake` grid, a 2D triangle grid is used. As the
    scaling for cell volumes between a raidal and a triangular grid is linear, the
    radial solution can be recovered. This function calculates the ratio

    .. math::

        r_{radial_grid} / x_{triangle_grid},

    where :math:`x_{triangle_grid}` is the altitude of the triangle, s.t. the solution
    on the triangle grid is equal to the solution on a radial grid with the given cell
    radii.

    Args:
        theta (ArrayLike): Angle of the triangle grid. Default is :math:`\pi/3`.

    Returns:
        ArrayLike: :math:`r_{radial_grid} / x_{triangle_grid}`

    """
    theta = np.asarray(theta)
    return 2 * np.tan(theta / 2) / theta


def equivalent_well_block_radius(delta_x: ArrayLike) -> ArrayLike:
    """Calculate the equivalent well block radius for a given quadratic cell size.

    Args:
        delta_x (ArrayLike): _description_

    Returns:
        (ArrayLike): _description_

    """
    delta_x = np.asarray(delta_x)
    return R_E_RATIO * delta_x


def cell_size(radii: ArrayLike) -> ArrayLike:
    """Calculate the cell size for a given equivalent well block radius.

    Args:
        delta_x (ArrayLike): _description_

    Returns:
        (ArrayLike): _description_

    """
    radii = np.asarray(radii)
    return radii / R_E_RATIO


def peaceman_WI(  # pylint: disable=C0103
    k_h: ArrayLike, r_e: ArrayLike, r_w: ArrayLike, rho: ArrayLike, mu: ArrayLike
) -> ArrayLike:
    r"""Compute the well productivity index (adjusted for density and viscosity)
    from the Peaceman well model.

    .. math::

        WI = \frac{2\pi hk\frac{\mu}{\rho}}{\ln(r_e/r_w)}

    Args:
        k_h (ArrayLike): Permeability times the cell thickness. Unit: [m^3].
        r_e (ArrayLike): Equivalent well-block radius. Needs to have the same unit as ``r_w``.
        r_w (ArrayLike): Wellbore radius. Needs to have the same unit as ``r_e``.
        rho (ArrayLike): Density. Unit: [kg/m^3].
        mu (ArrayLike): Viscosity. Unit: [Pa*s].

    Returns:
        WI (ArrayLike): :math:`WI`. Unit: [m*s].

    Raises:
        ValueError: If r_w is zero for any point.

    """
    k_h = np.asarray(k_h)
    r_e = np.asarray(r_e)
    r_w = np.asarray(r_w)
    rho = np.asarray(rho)
    mu = np.asarray(mu)

    if np.any(r_w == 0):
        raise ValueError("r_w cannot be zero")
    WI = (2 * math.pi * k_h) / (np.log(r_e / r_w))
    return WI * rho / mu


def two_phase_peaceman_WI(  # pylint: disable=C0103
    k_h: ArrayLike,
    r_e: ArrayLike,
    r_w: ArrayLike,
    rho_1: ArrayLike,
    mu_1: ArrayLike,
    k_r1: ArrayLike,
    rho_2: ArrayLike,
    mu_2: ArrayLike,
    k_r2: ArrayLike,
) -> ArrayLike:
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
        k_h (ArrayLike): Permeability times the cell thickness. Unit: [m^3].
        r_e (ArrayLike): Equivalent well-block radius. Needs to have the same unit as
            ``r_w``.
        r_w (ArrayLike): Wellbore radius. Needs to have the same unit as ``r_e``.
        rho_1 (ArrayLike): Density of phase 1. Unit: [kg/m^3].
        mu_1 (ArrayLike): Viscosity of phase 1. Unit: [Pa*s].
        k_r1 (ArrayLike): Relative permeability of phase 1.
        rho_2 (ArrayLike): Density of phase 2. Unit: [kg/m^3].
        mu_2 (ArrayLike): Viscosity of phase 2. Unit: [Pa*s].
        k_r2 (ArrayLike): Relative permeability of phase 2.

    Returns:
        WI (ArrayLike): :math:`WI`. Unit: [m*s].

    Raises:
        ValueError: If ``r_w`` is zero for any point.

    """
    k_h = np.asarray(k_h)
    r_e = np.asarray(r_e)
    r_w = np.asarray(r_w)
    rho_1 = np.asarray(rho_1)
    mu_1 = np.asarray(mu_1)
    k_r1 = np.asarray(k_r1)
    rho_2 = np.asarray(rho_2)
    mu_2 = np.asarray(mu_2)
    k_r2 = np.asarray(k_r2)

    if np.any(r_w == 0):
        raise ValueError("r_w cannot be zero")
    total_mobility: ArrayLike = (k_r1 * rho_1) / mu_1 + (k_r2 * rho_2) / mu_2
    WI = (2 * math.pi * k_h) / (np.log(r_e / r_w))
    return WI * total_mobility


def data_WI(
    q: ArrayLike,
    p_w: ArrayLike,
    p_gb: ArrayLike,
    well_type: Literal["injector", "producer"] = "injector",
) -> ArrayLike:  # pylint: disable=C0103
    r"""Compute the well productivity index from given data.

    .. math::
        WI = \frac{q}{p_w - p_{gb}

    Args:
        q (ArrayLike): Injection rate. Unit: [m^3/s].
        p_w (ArrayLike): Bottom hole pressure. Unit: [Pa].
        p_gb (ArrayLike): Grid block pressure. Unit: [Pa].
        well_type (Literal["injector", "producer], optional): Calculate WI for injector
        or producer. Defaults to ``"injector"``.

    Returns:
        WI (ArrayLike): :math:`WI`. Unit: [m^4*s/kg].

    Raises:
        ValueError: If bottom hole pressure and grid block pressure are equal for any
            point.

    """
    q = np.asarray(q)
    p_w = np.asarray(p_w)
    p_gb = np.asarray(p_gb)

    if well_type == "injector":
        delta_p: ArrayLike = p_w - p_gb
    else:
        delta_p = p_gb - p_w
    if np.any(delta_p == 0):
        raise ValueError("p_w and p_gb cannot be equal")
    WI = q / delta_p
    return WI


def co2brinepvt(
    pressure: float,
    temperature: float,
    phase_property: Literal["density", "viscosity"],
    phase: Literal["CO2", "water"],
    OPM: pathlib.Path,
) -> float:
    """Call OPM's ``co2brinepvt`` to calculate density/viscosity.

    Args:
        pressure (float): Unit: [Pa].
        temperature (float): Unit: [K].
        property (Literal["density", "viscosity"]): Phase property to return.
        phase (Literal["CO2", "water"]): Phase of interest.
        OPM: (pathlib.Path): Path to OPM installation.

    Returns:
        quantity (float): Density (unit: [kg/m^3]) or viscosity (unit: [Pa*s])

    """
    CO2BRINEPVT: pathlib.Path = OPM / "build/opm-common/bin/co2brinepvt"
    with subprocess.Popen(
        [
            str(CO2BRINEPVT),
            phase_property,
            phase if phase == "CO2" else "brine",
            str(pressure),
            str(temperature),
        ],
        stdout=subprocess.PIPE,
    ) as proc:
        # Ignore mypy complaining.
        value = float(proc.stdout.read())  # type: ignore
    return value


def hydrostatic_fluid(
    rho: ArrayLike,
    height: ArrayLike,
    gravity: ArrayLike = units.GRAVITATIONAL_ACCELERATION,
) -> ArrayLike:
    r"""
    Calculate the pressure due to hydrostatic fluid.

    This function calculates the pressure due to hydrostatic fluid using the formula:

    ..math::

        P = rho * g * h,

    where :math:`P` is the pressure,
    :math:`rho` is the fluid density,
    :math:`g` is the acceleration due to gravity, and
    :math:`h` is the height.

    Args:
        rho (ArrayLike): Fluid density. Unit [kg/m^3].
        height (ArrayLike): Height of the fluid column. Unit [m].
        gravity (ArrayLike, optional): Acceleration due to gravity. Unit [m/s^2].
            Defaults to ``units.GRAVITATIONAL_ACCELERATION``, i.e., :math:`\approx 9.8`.

    Returns:
        ArrayLike: Hydrostatic pressure at the given height. Unit [Pa].

    Examples:
        >>> hydrostatic_fluid(1000, 10)
        98067.0

    """
    # Convert to arrays to allow broadcasting
    rho = np.asarray(rho)
    height = np.asarray(height)

    # Convert ``None`` values in the ``gravity`` array to default values.
    # If the input is ``None``, use the default gravity.
    gravity = np.where(
        np.isnan(np.asarray(gravity, dtype=float)),
        np.full(
            np.broadcast_shapes(rho.shape, height.shape),
            units.GRAVITATIONAL_ACCELERATION,
        ),
        np.asarray(gravity, dtype=float),
    )

    return rho * gravity * height


def hydrostatic_gas(
    reference_pressure: ArrayLike,
    height: ArrayLike,
    temperature: ArrayLike,
    molecule_mass: ArrayLike,
    gravity: ArrayLike = units.GRAVITATIONAL_ACCELERATION,
) -> ArrayLike:
    r"""
    Calculate the pressure due to a column of gas in hydrostatic equilibrium.

    This function calculates the pressure due to a column of gas in hydrostatic equilibrium
    using the ideal gas law and the hydrostatic equilibrium formula. The formula is:

    ..math::

        P = P_0 * e^((-m * g * h) / (R^* * T)),

    where
    :math:`P`is the pressure,
    :math:`P_0` is the reference pressure,
    :math:`m`is the molecular mass of the gas,
    :math:`g`is the acceleration due to gravity,
    :math:`h`is the height,
    :math:`R^*`is the universal gas constant, and
    :math:`T`is the temperature.

    Args:
        reference_pressure (ArrayLike): Reference pressure at height 0. Unit [Pa].
        height (ArrayLike): Height of the gas column. Unit [m].
        temperature (ArrayLike): Temperature. Unit [K].
        molecule_mass (ArrayLike): Molecular mass of the gas. Unit [kg/mol].
        gravity (ArrayLike, optional): Acceleration due to gravity. Unit [m/s^2].
        Defaults to ``units.GRAVITATIONAL_ACCELERATION``, i.e., :math:`\approx 9.8`.

    Returns:
        ArrayLike: Hydrostatic pressure at the given height. Unit [Pa].

    Examples:
        >>> hydrostatic_gas(101325, 5000, 300, 0.029, 9.81)
        75819.90376642203

    """
    # Convert to arrays to allow broadcasting
    reference_pressure = np.asarray(reference_pressure)
    height = np.asarray(height)
    temperature = np.asarray(temperature)
    molecule_mass = np.asarray(molecule_mass)

    # Convert ``None`` values in the ``gravity`` array to default values.
    # If the input is ``None``, use the default gravity.
    gravity = np.where(
        np.isnan(np.asarray(gravity, dtype=float)),
        np.full(
            np.broadcast_shapes(
                reference_pressure.shape,
                height.shape,
                temperature.shape,
                molecule_mass.shape,
            ),
            units.GRAVITATIONAL_ACCELERATION,
        ),
        np.asarray(gravity, dtype=float),
    )

    factor: ArrayLike = math.e ** (
        (-molecule_mass * gravity * height)
        / (units.UNIVERSAL_GAS_CONSTANT * temperature)
    )
    return reference_pressure * factor


def area_squaredcircle(radius: ArrayLike, sidelength: ArrayLike) -> ArrayLike:
    """
    Calculate the area that lies both inside a circle and inside a square centered at
    the origin.

    Args:
        radius (ArrayLike): The radius of the circle.
        sidelength (ArrayLike): The sidelength of the square.

    Returns:
        ArrayLike: The calculated area.

    Raises:
        ValueError: If ``radius`` or ``sidelength`` contain a negative value.

    Examples:
        >>> area_squaredcircle(3.0, 3.0)
        9.0  # Area of a sqare with sidelength 3.0

        >>> area_squaredcircle(2.0, 4.0)
        12.566370614359172  # Area of a circle with radius 2.0

        >>> area_squaredcircle(2.0, 3.0)
        6.283185307179586  # Area inside a  2.0

    """
    # Convert to arrays to allow broadcasting
    radius = np.asarray(radius)
    sidelength = np.asarray(sidelength)

    if np.any(radius < 0):
        raise ValueError("Radius cannot be negative.")
    if np.any(sidelength < 0):
        raise ValueError("Sidelength cannot be negative.")

    # Square (base case)
    result: np.ndarray = np.broadcast_to(
        sidelength**2, (np.broadcast_shapes(radius.shape, sidelength.shape))
    )

    # Circle
    result = np.where(radius <= sidelength / 2, math.pi * radius**2, result)

    # Squared circle segment
    theta: np.ndarray = np.arccos(sidelength / (2 * radius))
    y: np.ndarray = radius * np.sin(theta)
    squaredcircle: np.ndarray = 8 * (
        (math.pi / 4 - theta) * (radius**2) / 2 + y * sidelength / 4
    )
    result = np.where(
        np.logical_and(radius > sidelength / 2, radius < sidelength / math.sqrt(2)),
        squaredcircle,
        result,
    )
    return result
