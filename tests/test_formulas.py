# pylint: skip-file
"""Test the ``utils.formulas`` module."""
from __future__ import annotations

import math
from typing import Optional

import numpy as np
import pytest
from numpy.typing import ArrayLike

from pyopmnearwell.utils.formulas import (
    area_squaredcircle,
    data_WI,
    hydrostatic_fluid,
    hydrostatic_gas,
    peaceman_matrix_WI,
    peaceman_WI,
    two_phase_peaceman_WI,
)


@pytest.mark.parametrize(
    "k_h, r_e, r_w, expected",
    [
        (1e-12, 100.0, 1.0, 2 * math.pi * 1e-12 / math.log(100.0)),
        (1e-11, 200.0, 0.5, 2 * math.pi * 1e-11 / math.log(400.0)),
        (1e-11, 250.0, 0.5, 2 * math.pi * 1e-11 / math.log(500.0)),
        (1e-13, 200.0, 0.5, 2 * math.pi * 1e-13 / math.log(400.0)),
        (
            np.array([1e-12, 1e-11]),
            np.array([100.0, 200.0]),
            np.array([1.0, 0.5]),
            np.array(
                [
                    2 * math.pi * 1e-12 / math.log(100.0),
                    2 * math.pi * 1e-11 / math.log(400.0),
                ]
            ),
        ),
        (
            np.array([1e-11, 1e-13]),
            np.array([250.0, 200.0]),
            np.array([0.5, 0.5]),
            np.array(
                [
                    2 * math.pi * 1e-11 / math.log(500.0),
                    2 * math.pi * 1e-13 / math.log(400.0),
                ]
            ),
        ),
        (1e-12, 0.0, 1.0, ValueError),
        (1e-12, 1.0, 0.0, ValueError),
        (1e-12, 1.0, -5.5, ValueError),
        (
            np.array([1e-12, 1e-11, 1e-10]),
            np.array([100.0, 200.0, 300.0]),
            np.array([1.0, 0.5, 0.0]),
            ValueError,
        ),
        (
            np.array([1e-12, 1e-11, 1e-10]),
            np.array([100.0, 0.5, 300.0]),
            np.array([1.0, 0.5, 1.0]),
            ValueError,
        ),
    ],
)
def test_peaceman_matrix_WI(
    k_h: ArrayLike, r_e: ArrayLike, r_w: ArrayLike, expected: ArrayLike | ValueError
):
    if expected is ValueError:
        with pytest.raises(ValueError):
            result = peaceman_matrix_WI(k_h, r_e, r_w)
    else:
        result = peaceman_matrix_WI(k_h, r_e, r_w)
        assert np.allclose(result, expected, rtol=1e-7)  # type: ignore


@pytest.mark.parametrize(
    "k_h, r_e, r_w, rho, mu, expected",
    [
        (1e-12, 100.0, 1.0, 1000.0, 0.001, 1.36438e-6),
        (1e-11, 200.0, 0.5, 800.0, 0.002, 4.19476e-6),
        (1e-11, 250.0, 0.5, 50.0, 0.002, 2.52759e-7),
        (1e-13, 200.0, 0.5, 20.0, 0.006, 3.49563e-10),
        (
            np.array([1e-12, 1e-11]),
            np.array([100.0, 200.0]),
            np.array([1.0, 0.5]),
            np.array([1000.0, 800.0]),
            np.array([0.001, 0.002]),
            np.array([1.36438e-6, 4.19476e-6]),
        ),
        (
            np.array([1e-11, 1e-13]),
            np.array([250.0, 200.0]),
            np.array([0.5, 0.5]),
            np.array([50.0, 20.0]),
            np.array([0.002, 0.006]),
            np.array([2.52759e-7, 3.49563e-10]),
        ),
    ],
)
def test_peaceman_WI(
    k_h: ArrayLike,
    r_e: ArrayLike,
    r_w: ArrayLike,
    rho: ArrayLike,
    mu: ArrayLike,
    expected: ArrayLike,
):
    """Test the Peaceman formulas versus several results calculated by hand."""
    result = peaceman_WI(k_h, r_e, r_w, rho, mu)
    assert np.allclose(result, expected, rtol=1e-7)


@pytest.mark.parametrize(
    "k_h, r_e, r_w, rho_1, mu_1, k_r1, rho_2, mu_2, k_r2, expected",
    [
        (1e-12, 100.0, 1.0, 1000.0, 0.001, 0.5, 30.0, 0.01, 0.15, 6.82802e-7),
        (1e-11, 200.0, 0.5, 800.0, 0.002, 0.4, 500.0, 0.0002, 0.3, 9.54307e-6),
        (1e-11, 250.0, 0.5, 50.0, 0.002, 0.7, 500.0, 0.01, 0.1, 2.27483e-7),
        (1e-13, 200.0, 0.5, 20.0, 0.006, 0.9, 1000.0, 0.1, 0.01, 3.25084e-10),
        (
            np.array([1e-12, 1e-11]),
            np.array([100.0, 200.0]),
            np.array([1.0, 0.5]),
            np.array([1000.0, 800.0]),
            np.array([0.001, 0.002]),
            np.array([0.5, 0.4]),
            np.array([30.0, 500.0]),
            np.array([0.01, 0.0002]),
            np.array([0.15, 0.3]),
            np.array([6.82802e-7, 9.54307e-6]),
        ),
        (
            np.array([1e-11, 1e-13]),
            np.array([250.0, 200.0]),
            np.array([0.5, 0.5]),
            np.array([50.0, 20.0]),
            np.array([0.002, 0.006]),
            np.array([0.7, 0.9]),
            np.array([500.0, 1000.0]),
            np.array([0.01, 0.1]),
            np.array([0.1, 0.01]),
            np.array([2.27483e-7, 3.25084e-10]),
        ),
    ],
)
def test_two_phase_peaceman_WI(
    k_h: ArrayLike,
    r_e: ArrayLike,
    r_w: ArrayLike,
    rho_1: ArrayLike,
    mu_1: ArrayLike,
    k_r1: ArrayLike,
    rho_2: ArrayLike,
    mu_2: ArrayLike,
    k_r2: ArrayLike,
    expected: ArrayLike,
):
    """Test the Peaceman formulas versus several results calculated by hand."""
    result = two_phase_peaceman_WI(k_h, r_e, r_w, rho_1, mu_1, k_r1, rho_2, mu_2, k_r2)
    assert np.allclose(result, expected, rtol=1e-7)


@pytest.mark.parametrize(
    "q, p_w, p_gb, expected",
    [
        (0.1, 1000000, 700000.0, (1 / 3) * 1e-6),
        (0.02, 300000.0, 250000.0, 4e-7),
        (0.0045, 1035700.0, 609700.0, 3 / 284000000),
        (
            np.array([0.1, 0.02, 0.0045]),
            np.array([1000000, 300000.0, 1035700.0]),
            np.array([700000.0, 250000.0, 609700.0]),
            np.array([(1 / 3) * 1e-6, 4e-7, 3 / 284000000]),
        ),
    ],
)
def test_data_WI(q: ArrayLike, p_w: ArrayLike, p_gb: ArrayLike, expected: ArrayLike):
    result = data_WI(q, p_w, p_gb)
    assert np.allclose(result, expected, rtol=1e-7)


# Test cases for co2brinepvt (you may need to mock subprocess.Popen for this)
# Mocking subprocess.Popen is recommended for testing external commands.
# Example: https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock
# @pytest.fixture
# def opm_cov2brinepvt():
#     # TODO: Add tests
#     pass


# @pytest.mark.parametrize(
#     "pressure, temperature, phase, expected_density, expected_viscosity",
#     [
#         (10, 25, "CO2", 0.9, 0.001),
#         (50, 50, "water", 1.1, 0.002),
#         (100, 75, "CO2", 1.2, 0.003),
#     ],
# )
# def test_co2brinepvt(
#     pressure, temperature, phase, expected_density, expected_viscosity
# ):
#     result = co2brinepvt(pressure, temperature, phase)
#     assert result.density == pytest.approx(expected_density, rel=1e-2)
#     assert result.viscosity == pytest.approx(expected_viscosity, rel=1e-2)


@pytest.mark.parametrize(
    "rho, height, gravity, expected",
    [
        (1000, 10, None, 98067.0),
        (1200, 15, None, 176520.6),
        (800, 20, 9.75, 156000.0),
        (
            np.array([1000, 1200]),
            np.array([10, 15]),
            None,
            np.array([98067.0, 176520.6]),
        ),
        (
            np.array([1200, 800]),
            np.array([15, 20]),
            np.array([None, 9.75]),
            np.array([176520.6, 156000.0]),
        ),
    ],
)
def test_hydrostatic_fluid(
    rho: ArrayLike, height: ArrayLike, gravity: Optional[ArrayLike], expected: ArrayLike
):
    args = locals()
    filtered_args = {
        key: value
        for key, value in args.items()
        if value is not None and key != "expected"
    }
    result = hydrostatic_fluid(**filtered_args)
    assert np.allclose(result, expected, rtol=1e-7)


@pytest.mark.parametrize(
    "reference_pressure, height, temperature, molecule_mass, gravity, expected",
    [
        (101325, 1000, 300, 0.029, None, 90406.59923388921),
        (80000, 200, 400, 0.032, None, 78504.42842124676),
        (120000, 30, 350, 0.018, 9.3, 119793.09020997149),
        (
            np.array([101325, 80000, 120000]),
            np.array([1000, 200, 30]),
            np.array([300, 400, 350]),
            np.array([0.029, 0.032, 0.018]),
            np.array([None, None, 9.3]),
            np.array([90406.59923388921, 78504.42842124676, 119793.09020997149]),
        ),
    ],
)
def test_hydrostatic_gas(
    reference_pressure: ArrayLike,
    height: ArrayLike,
    temperature: ArrayLike,
    molecule_mass: ArrayLike,
    gravity: Optional[ArrayLike],
    expected: ArrayLike,
):
    args = locals()
    filtered_args = {
        key: value
        for key, value in args.items()
        if value is not None and key != "expected"
    }
    result = hydrostatic_gas(**filtered_args)
    assert np.allclose(result, expected, rtol=1e-7)


@pytest.mark.parametrize(
    "radius, sidelength, expected",
    [
        (3.0, 3.0, 9.0),  # Square
        (2.0, 4.0, math.pi * 2.0**2),  # Circle
        (1.8, 3.0, 8.5582001770659736),  # Circular sector inside a square
        (-1.0, 5.0, ValueError),  # Invalid radius
        (2.0, -3.0, ValueError),  # Invalid sidelength
        (
            np.array([3.0, 2.0, 1.8, -1.0, 2.0]),
            np.array([3.0, 4.0, 3.0, 5.0, -3.0]),
            np.array(
                [9.0, math.pi * 2.0**2, 8.5582001770659736, ValueError, ValueError]
            ),
        ),
    ],
)
def test_area_squaredcircle(
    radius: ArrayLike, sidelength: ArrayLike, expected: ArrayLike | ValueError
):
    if np.any(np.asarray(expected) == ValueError):
        with pytest.raises(ValueError):
            area_squaredcircle(radius, sidelength)
    else:
        result = area_squaredcircle(radius, sidelength)
        # Ignore mypy complaining. We checked that ``expected`` is not ``ValueError``.
        assert np.allclose(result, expected, rtol=1e-7)  # type: ignore
