"""Provide useful mathematical formulas for reservoir modelling."""

import math


def peaceman_WI(  # pylint: disable=C0103
    k_h: float, r_e: float, r_w: float, rho: float, mu: float
) -> float:
    r"""Compute the well productivity index (adjusted for density and viscosity)
    from the Peaceman well model.

    .. math::
        WI\cdot\frac{\mu}{\rho} = \frac{2\pi hk}{\ln (r_e/r_w)}

    Parameters:
        k_h: Permeability times the cell thickness (thickness fix to 1 m). Needs to be
        in [m^3].
        r_e: Equivalent well-block radius. Needs to have the same unit as ``r_w``.
        r_w: Wellbore radius. Needs to have the same unit as ``r_e``.
        rho: Density. Needs to be in [kg/m^3].
        mu: Viscosity. Needs to be in [Pa*s].

    Returns:
        Well index :math:`WI`. In [m*s].

    """
    WI = (2 * math.pi * k_h) / (math.log(r_e / r_w))
    return WI * rho / mu


def data_WI(q: float, p_w: float, p_gb: float) -> float:  # pylint: disable=C0103
    r"""Compute the well productivity index from given data.

    .. math::
        WI = \frac{q}{p_w - p_{gb}

    Parameters:
        q: Injection rate. Needs to be in [m^3/s].
        p_w: Bottom hole pressure. Needs to be in [Pa].
        p_gb: Grid block pressure. Needs to be in [Pa].

    Returns:
        Well index :math:`WI`. In [m^4*s/kg].

    """
    WI = q / (p_w - p_gb)
    return WI
