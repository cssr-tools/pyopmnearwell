"""Test the ``utils.formulas`` module.

Test the Peaceman formulas versus several results calculated by hand. 

"""

import numpy as np
import pytest

from pyopmnearwell.utils.formulas import (
    co2brinepvt,
    data_WI,
    hydrostatic_fluid,
    hydrostatic_gas,
    peaceman_WI,
    two_phase_peaceman_WI,
)


@pytest.mark.parametrize(
    "k_h, r_e, r_w, rho, mu, expected_result",
    [
        (1e-12, 100.0, 1.0, 1000.0, 0.001, 1.36438e-6),
        (1e-11, 200.0, 0.5, 800.0, 0.002, 4.19476e-6),
        (1e-11, 250.0, 0.5, 50.0, 0.002, 2.52759e-7),
        (1e-13, 200.0, 0.5, 20.0, 0.006, 3.49563e-10),
    ],
)
def test_peaceman_WI(k_h, r_e, r_w, rho, mu, expected_result):
    result = peaceman_WI(k_h, r_e, r_w, rho, mu)
    assert pytest.approx(result, rel=1e-4) == expected_result


@pytest.mark.parametrize(
    "k_h, r_e, r_w, rho_1, mu_1, k_r1, rho_2, mu_2, k_r2, expected_result",
    [
        (1e-12, 100.0, 1.0, 1000.0, 0.001, 0.5, 30.0, 0.01, 0.15, 6.82802e-7),
        (1e-11, 200.0, 0.5, 800.0, 0.002, 0.4, 500.0, 0.0002, 0.3, 9.54307e-6),
        (1e-11, 250.0, 0.5, 50.0, 0.002, 0.7, 500.0, 0.01, 0.1, 2.27483e-7),
        (1e-13, 200.0, 0.5, 20.0, 0.006, 0.9, 1000.0, 0.1, 0.01, 3.25084e-10),
    ],
)
def test_two_phase_peaceman_WI(
    k_h, r_e, r_w, rho_1, mu_1, k_r1, rho_2, mu_2, k_r2, expected_result
):
    result = two_phase_peaceman_WI(k_h, r_e, r_w, rho_1, mu_1, k_r1, rho_2, mu_2, k_r2)
    assert pytest.approx(result, rel=1e-4) == expected_result


@pytest.mark.parametrize(
    "q, p_w, p_gb, expected_result",
    [
        (0.1, 1000000, 700000.0, (1 / 3) * 1e-6),
        (0.02, 300000.0, 250000.0, 4e-7),
        (0.0045, 1035700.0, 609700.0, 3 / 284000000),
    ],
)
def test_data_WI(q, p_w, p_gb, expected_result):
    result = data_WI(q, p_w, p_gb)
    assert pytest.approx(result, rel=1e-4) == expected_result


# Test cases for co2brinepvt (you may need to mock subprocess.Popen for this)
# Mocking subprocess.Popen is recommended for testing external commands.
# Example: https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock
@pytest.fixture
def opm_cov2brinepvt():
    # TODO
    pass


# @pytest.mark.parametrize(
#     "pressure, temperature",
#     [
#         (pressure, temperature)
#         for pressure, temperature in zip(
#             np.random.uniform(10000, 50000000, 50), np.random.uniform(250, 400, 50)
#         )
#     ],
# )
# @pytest.mark.parametrize("property", ["density", "viscosity"])
# @pytest.mark.parametrize("phase", ["CO2", "water"])
# def test_co2brinepvt(opm_cov2brinepvt) -> None:
#     # TODO
#     pass


@pytest.mark.parametrize(
    "rho, height, gravity, expected_pressure",
    [
        (1000, 10, None, 98067.0),
        (1200, 15, None, 176520.6),
        (800, 20, 9.75, 156000.0),
    ],
)
def test_hydrostatic_fluid(rho, height, gravity, expected_pressure):
    args = locals()
    filtered_args = {
        key: value
        for key, value in args.items()
        if value is not None and key != "expected_pressure"
    }
    result = hydrostatic_fluid(**filtered_args)
    assert pytest.approx(result, rel=1e-7) == expected_pressure


@pytest.mark.parametrize(
    "reference_pressure, height, temperature, molecule_mass, gravity, expected_pressure",
    [
        (101325, 1000, 300, 0.029, None, 90406.59923388921),
        (80000, 200, 400, 0.032, None, 78504.42842124676),
        (120000, 30, 350, 0.018, 9.3, 119793.09020997149),
    ],
)
def test_hydrostatic_gas(
    reference_pressure, height, temperature, molecule_mass, gravity, expected_pressure
):
    args = locals()
    filtered_args = {
        key: value
        for key, value in args.items()
        if value is not None and key != "expected_pressure"
    }
    result = hydrostatic_gas(**filtered_args)
    assert pytest.approx(result, rel=1e-7) == expected_pressure
