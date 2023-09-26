"""Test the ``utils.formulas`` module.

Test the Peaceman formulas versus several results calculated by hand. 

"""

import pytest

from pyopmnearwell.utils.formulas import (
    co2brinepvt,
    data_WI,
    peaceman_WI,
    two_phase_peaceman_WI,
)


# Test cases for peaceman_WI
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


# Test cases for two_phase_peaceman_WI
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


# Test cases for data_WI
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
