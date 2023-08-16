"""Test the ``utils.units`` module."""
import pytest

import pyopmnearwell.utils.units as units


def test_permeability() -> None:
    """Test that the permeability unit conversions are multiplicative inverses."""
    assert units.M2_TO_MILIDARCY * units.MILIDARCY_TO_M2 == 1.0


def test_pressure() -> None:
    """Test that the pressure unit conversions are multiplicative inverses."""
    assert units.PASCAL_TO_BAR * units.BAR_TO_PASCAL == 1.0


def test_temperature() -> None:
    """Test that the temperature unit conversions are additive inverses."""
    assert units.CELSIUS_TO_KELVIN + units.KELVIN_TO_CELSIUS == 0.0
