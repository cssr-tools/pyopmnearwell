"""Test the ``ml.ensemble`` module."""
import os
import shutil
import tempfile
from collections.abc import Iterator
from contextlib import nullcontext as does_not_raise
from typing import Any
from unittest.mock import mock_open, patch

import numpy as np
import pytest

from pyopmnearwell.ml.ensemble import create_ensemble, run_ensemble, setup_ensemble
from pyopmnearwell.utils import units

dir = os.path.dirname(__file__)

REPORT_STEPS: int = 20
NUM_CELLS: int = 100


@pytest.fixture(scope="session")
def temp_ensemble_dir(tmp_path_factory) -> Iterator[str]:
    """Create and return a temporary directory for testing."""
    dirname = tmp_path_factory.mktemp("ensemble")
    os.mkdir(os.path.join(dirname, "preprocessing"))
    os.mkdir(os.path.join(dirname, "jobs"))
    yield dirname
    # shutil.rmtree(dirname)


@pytest.fixture(scope="session")
def ensemble_dict() -> dict[str, Any]:
    return {"ensemble": None}


@pytest.fixture
def runspecs():
    pass


# Test cases for create_ensemble, setup_ensemble, run_ensemble
@pytest.mark.parametrize(
    "runspecs",
    [
        (
            {
                "npoints": 12,
                "npruns": 3,
                "variables": {
                    "PRESSURE": (
                        50.9 * units.BAR_TO_PASCAL,
                        70.5 * units.BAR_TO_PASCAL,
                        3,
                    ),
                    "TEMPERATURE": (20.5, 30.5, 2),
                    "PERMX": (700, 950, 2),
                },
                "constants": {"FLOW": "..", "PERMZ": 1.3, "INJECTION_RATE": 20},
            }
        ),
        (
            {
                "npoints": 10,
                "npruns": 5,
                "variables": {
                    "PRESSURE": (
                        30.5 * units.BAR_TO_PASCAL,
                        70.5 * units.BAR_TO_PASCAL,
                        20,
                    ),
                    "TEMPERATURE": (-20.5, 10.5, 10),
                    "PERMX": (100.5, 105.5, 20),
                },
                "constants": {"FLOW": "..", "PERMZ": 0.7, "INJECTION_RATE": 10},
            }
        ),
        (
            {
                "npoints": 200,
                "npruns": 10,
                "variables": {
                    "PRESSURE": (0 * units.BAR_TO_PASCAL, 10 * units.BAR_TO_PASCAL, 5),
                    "TEMPERATURE": (-20.1, 0, 5),
                    "PERMX": (1, 1.5, 5),
                },
                "constants": {"FLOW": "..", "PERMZ": 5, "INJECTION_RATE": 5},
            }
        ),
    ],
)
class TestEnsemble:
    @pytest.mark.parametrize(
        "expected_exception",
        [
            (does_not_raise()),
            (does_not_raise()),
            (pytest.raises(ValueError)),
        ],
    )
    def test_create_ensemble(
        self,
        runspecs: dict[str, Any],
        ensemble_dict: dict[str, Any],
        expected_exception,
    ) -> None:
        # Skip invalid ``pytest.mark.parametrize`` combinations.
        if (
            type(expected_exception) is type(does_not_raise())
            and runspecs["npoints"] == 200
        ) or (
            type(expected_exception) is type(pytest.raises(ValueError))
            and runspecs["npoints"] < 20
        ):
            pytest.skip("Invalid case.")

        with expected_exception:
            ensemble: list[dict[str, Any]] = create_ensemble(runspecs)
            max_values: dict[str, np.ndarray] = {}
            min_values: dict[str, np.ndarray] = {}
            for variable, (min, max, _) in runspecs["variables"].items():
                max_values[variable] = max
                min_values[variable] = min
            assert len(ensemble) == runspecs["npoints"]
            for member in ensemble:
                for variable, value in member.items():
                    if variable in max_values:
                        assert value <= max_values[variable]
                        assert value >= min_values[variable]
            ensemble_dict["ensemble"] = ensemble

    def test_setup_assemble(
        self, runspecs: dict[str, Any], ensemble_dict: dict[str, Any], temp_ensemble_dir
    ) -> None:
        # Skip invalid test cases.
        if runspecs["npoints"] == 200:
            pytest.skip("Invalid case.")

        ensemble = ensemble_dict["ensemble"]
        setup_ensemble(
            temp_ensemble_dir, ensemble, os.path.join(dir, "test_ensemble.mako")
        )
        ensemble_files = [
            file
            for file in os.listdir(os.path.join(temp_ensemble_dir, "preprocessing"))
            if file.startswith("RUN")
        ]
        # Check that all ensemble files were generated.
        assert len(ensemble) == len(ensemble_files)
        for member_file in ensemble_files:
            assert member_file.startswith("RUN_")
            assert member_file.endswith(".DATA")

    def test_run_ensemble(self, runspecs: dict[str, Any], temp_ensemble_dir) -> None:
        """
        Test the `run_ensemble` for various inputs.

        Args:
            temp_directory (str): Temporary directory path to store the ensemble runs.

        Asserts:
            - The lists in the returned dictionary have the correct length (npoints)
            - The arrays in the returned dictionary have the correct type (numpy.ndarray).
            - The shape of arrays matches expectations for various npoints and npruns.
        """
        # Skip invalid test cases.
        if runspecs["npoints"] == 200:
            pytest.skip("Invalid case.")

        ecl_keywords = ["PRESSURE", "SGAS"]
        summary_keywords = ["W1BHP"]
        OPM: str = "/home/peter/Documents/2023_CEMRACS/opm"
        FLOW: str = f"{OPM}/build/opm-simulators/bin/flow"

        with patch("builtins.open", mock_open()):
            data = run_ensemble(
                FLOW, temp_ensemble_dir, runspecs, ecl_keywords, summary_keywords
            )

        # Ensure that the returned data are ``np.ndarrays``.
        for keyword, lst in data.items():
            assert len(lst) == runspecs["npoints"]
            for array in lst:
                assert isinstance(array, np.ndarray)

        # Ensure that the data arrays have the correct shape.
        for keyword, array in data.items():
            if keyword in ecl_keywords:
                expected_shape: tuple = (
                    REPORT_STEPS,
                    NUM_CELLS,
                )  # 10 ensemble members for each keyword.
            else:
                expected_shape = (0,)  # No data for summary keywords.
            assert array.shape == expected_shape


def test_calculate_radii():
    pass


def test_calculate_WI():
    pass


def test_extract_features():
    pass


if __name__ == "__main__":
    pytest.main()
