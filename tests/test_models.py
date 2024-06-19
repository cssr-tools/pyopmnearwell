"""Test ``pyopmnearwell`` for different models."""

import os
import pathlib

import pytest

dirname: pathlib.Path = pathlib.Path(__file__).parent


@pytest.mark.parametrize(
    "run_models,expected",
    [
        ("input", "output/INPUT.UNRST"),
        ("co2core", "output/CO2CORE.UNRST"),
        ("co2eor", "output/CO2EOR.UNRST"),
        ("co2store", "postprocessing/pressure_2D.png"),
        ("h2store", "postprocessing/pressure_2D.png"),
        ("saltprec", "postprocessing/cumulative_saltprec.png"),
    ],
    indirect=["run_models"],
)
def test_models(run_models: tuple[str, pathlib.Path], expected: str) -> None:
    """Check that pyopmnearwell runs for the co2core, co2eor, co2store, and
    h2store decks in ```models``.

    Parameters:
        run_models: Output from the ``conftest.fixture_run_models`` fixture.
            Tuple containing the model name and the run path.
        expected: A file that should exist after pyopmnearwell was successfully run.

    """
    model, run_path = run_models
    os.chdir(run_path)
    assert (run_path / model / expected).exists()
