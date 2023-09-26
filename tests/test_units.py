"""Test the ``utils.units`` module.

The module is tested by checking that the unit conversion are inverses of each other.

"""
import pytest

import pyopmnearwell.utils.units as units


def test_permeability() -> None:
    """Test that the permeability unit conversions are multiplicative inverses."""
    assert units.M2_TO_MILIDARCY * units.MILIDARCY_TO_M2 == pytest.approx(1.0, rel=1e-4)


def test_pressure() -> None:
    """Test that the pressure unit conversions are multiplicative inverses."""
    assert units.PASCAL_TO_BAR * units.BAR_TO_PASCAL == pytest.approx(1.0, rel=1e-4)


def test_temperature() -> None:
    """Test that the temperature unit conversions are additive inverses."""
    assert units.CELSIUS_TO_KELVIN + units.KELVIN_TO_CELSIUS == pytest.approx(
        0.0, rel=1e-4
    )
