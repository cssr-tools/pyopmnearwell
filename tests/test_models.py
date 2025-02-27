"""Test ``pyopmnearwell`` for different models."""

import os
import pathlib

import pytest

dirname: pathlib.Path = pathlib.Path(__file__).parent


@pytest.mark.parametrize(
    "run_model,expected",
    [
        ("input", "output/INPUT.UNRST"),
        ("co2eor", "output/CO2EOR.UNRST"),
        ("co2store", "postprocessing/pressure_2D.png"),
        ("foam", "output/FOAM.UNRST"),
        ("h2store", "postprocessing/distance_from_well.png"),
        ("saltprec", "postprocessing/cumulative_saltprec.png"),
    ],
    indirect=["run_model"],
)
def test_models(run_model: tuple[str, pathlib.Path], expected: str) -> None:
    """Check that pyopmnearwell runs for the input, co2core, co2eor, co2store, foam,
    h2store, and saltprec decks in ```models``.

    The fixture runs pyopmnearwell via the command line.

    Args:
        run_model (tuple[str, pathlib.Path]): Output from the
            ``conftest.fixture_run_model`` fixture. Tuple containing the model name and
            the run path.
        expected (str): A file that should exist after pyopmnearwell was successfully
            run.

    """
    model, run_path = run_model
    os.chdir(run_path)
    assert (run_path / model / expected).exists()
