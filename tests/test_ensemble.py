# pylint: disable=missing-function-docstring, fixme
"""Test the ``ml.ensemble`` module."""

from __future__ import annotations

import itertools
import pathlib
from contextlib import nullcontext as does_not_raise
from typing import Any, Optional
from unittest.mock import mock_open, patch

import numpy as np
import pytest

from pyopmnearwell.ml.ensemble import (
    calculate_WI,
    create_ensemble,
    get_flags,
    integrate_fine_scale_value,
    memory_efficient_sample,
    run_ensemble,
    setup_ensemble,
)

TEST_ENSEMBLE_MAKO: pathlib.Path = pathlib.Path(__file__).parent / "test_ensemble.mako"

REPORT_STEPS: int = 20
NUM_CELLS: int = 100

rng: np.random.Generator = np.random.default_rng()


# Disable some pylint warnings for the ``TestEnsemble`` class. Some functions need
# unused arguments, because they rely on the connected fixtures being run.
# pylint: disable=unused-argument, invalid-name


# Test cases for create_ensemble, setup_ensemble, run_ensemble:
@pytest.mark.parametrize(
    "runspecs",
    [
        (
            {
                "npoints": 12,
                "npruns": 3,
                "variables": {
                    "PRESSURE": (
                        50.9,
                        70.5,
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
                        30.5,
                        70.5,
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
                    "PRESSURE": (0, 10, 5),
                    "TEMPERATURE": (-20.1, 0, 5),
                    "PERMX": (1, 1.5, 5),
                },
                "constants": {"FLOW": "..", "PERMZ": 5, "INJECTION_RATE": 5},
            }
        ),
    ],
    indirect=True,
)
# NOTE: The ``fixture_create_ensemble`` parametrization is only needed for
# ``test_create_ensemble`` and ``test_setup_ensemble``. It is ignored by
# ``test_run_ensemble``.
@pytest.mark.parametrize(
    "fixture_create_ensemble",
    [
        (does_not_raise()),
        (does_not_raise()),
        (pytest.raises(ValueError)),
    ],
    indirect=True,
)
# NOTE: The ``fixture_setup_ensemble`` parametrization is only needed for
# ``test_setup_ensemble`` and ``test_run_ensemble``. It is ignored by
# ``test_create_ensemble``.
@pytest.mark.parametrize(
    "fixture_setup_ensemble",
    itertools.product(*([[True, False]] * 3)),
    indirect=True,
)
class TestEnsemble:
    """Collected fixtures and test function functions to test ``create_ensemble``,
    ``setup_ensemble`` and ``run_ensemble``.

    Note: All three test functions need to access some common objects. This is done via
    the fixtures

    """

    @pytest.fixture(scope="class", name="runspecs")
    def fixture_runspecs(self, request) -> dict[str, Any]:
        return request.param

    @pytest.fixture(scope="class", name="fixture_create_ensemble")
    def fixture_create_ensemble(
        self, request, runspecs: dict[str, Any]
    ) -> Optional[list[dict[str, Any]]]:
        """Create and return ensemble.

        Args:
            request (_type_): _description_
            runspecs (_type_): _description_

        Returns:
            _type_: _description_

        """
        expected_exception = request.param
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
            return create_ensemble(runspecs)

    @pytest.fixture(scope="class", name="fixture_setup_ensemble")
    def fixture_setup_ensemble(
        self,
        request,
        fixture_create_ensemble: Optional[list[dict[str, Any]]],
        tmp_path_factory,
    ) -> Optional[pathlib.Path]:
        """Setup ensemble and return the folder path.

        Args:
            request (_type_): _description_
            runspecs (dict[str, Any]):
            fixture_create_ensemble (_type_): _description_
            tmp_path_factory (_type_): _description_

        Returns:
            _type_: _description_

        """
        if fixture_create_ensemble is not None:
            recalc_grid: bool = request.param[-3]
            recalc_tables: bool = request.param[-2]
            recalc_sections: bool = request.param[-1]

            # Create ensemble dir.
            dirname: pathlib.Path = tmp_path_factory.mktemp("ensemble")
            (dirname / "preprocessing").mkdir()

            setup_ensemble(
                dirname,
                fixture_create_ensemble,
                TEST_ENSEMBLE_MAKO,
                recalc_grid=recalc_grid,
                recalc_tables=recalc_tables,
                recalc_sections=recalc_sections,
            )
            return dirname
        return None

    def test_create_ensemble(
        self,
        runspecs: dict[str, Any],
        fixture_create_ensemble: Optional[list[dict[str, Any]]],
        fixture_setup_ensemble: Optional[pathlib.Path],
    ) -> None:
        if fixture_create_ensemble is not None:
            max_values: dict[str, np.ndarray] = {}
            min_values: dict[str, np.ndarray] = {}
            for variable, (min_value, max_value, _) in runspecs["variables"].items():
                max_values[variable] = max_value
                min_values[variable] = min_value
            assert len(fixture_create_ensemble) == runspecs["npoints"]
            for member in fixture_create_ensemble:
                for variable, value in member.items():
                    if variable in max_values:
                        assert value <= max_values[variable]
                        assert value >= min_values[variable]

    # TODO: For some reason, all these tests get skipped. Fix this!
    def test_setup_assemble(
        self,
        runspecs: dict[str, Any],
        fixture_create_ensemble: list[dict[str, Any]],
        fixture_setup_ensemble: pathlib.Path,
    ) -> None:
        # Skip invalid test cases.
        if runspecs["npoints"] == 200:
            pytest.skip("Invalid case.")
        # if fixture_create_ensemble is None:
        #     pytest.skip("Invalid case.")

        ensemble_folders: list[str] = [
            folder.name
            for folder in fixture_setup_ensemble.iterdir()
            if folder.name.startswith("runfiles")
        ]
        # Check that all ensemble files were generated.
        assert len(fixture_create_ensemble) == len(ensemble_folders)
        for member_folder in ensemble_folders:
            subfolders: list[str] = [
                file.name for file in (fixture_setup_ensemble / member_folder).iterdir()
            ]
            assert "preprocessing" in subfolders

            if member_folder.endswith("_0"):
                preprocessing_files: list[str] = [
                    file.name
                    for file in (
                        fixture_setup_ensemble / member_folder / "preprocessing"
                    ).iterdir()
                ]
                for file in [
                    "GEOLOGY.INC",
                    "GRID.INC",
                    "MULTPV.INC",
                    "REGIONS.INC",
                    "TABLES.INC",
                    "RUN_0.DATA",
                ]:
                    assert file in preprocessing_files
            else:
                runfiles: list[pathlib.Path] = list(
                    (fixture_setup_ensemble / member_folder / "preprocessing").iterdir()
                )
                assert len(runfiles) == 1
                runfile: pathlib.Path = runfiles[0]
                assert runfile.name.startswith("RUN_")
                assert runfile.name.endswith(".DATA")

    # TODO: For some reason, all these tests get skipped. Fix this!
    def test_run_ensemble(
        self,
        runspecs: dict[str, Any],
        fixture_create_ensemble: list[dict[str, Any]],
        fixture_setup_ensemble: pathlib.Path,
    ) -> None:
        """
        Test the `run_ensemble` for various inputs.

        Args:
            runspecs (dict[str, Any]):
            fixture_create_ensemble (list[dict[str, Any]]):
            fixture_setup_ensemble (pathlib.Path):

        Asserts:
            - The lists in the returned dictionary have the correct length (npoints)
            - The arrays in the returned dictionary have the correct type (numpy.ndarray).
            - The shape of arrays matches expectations for various npoints and npruns.

        """
        # Skip invalid test cases.
        if runspecs["npoints"] == 200:
            pytest.skip("Invalid case.")
        # if fixture_create_ensemble is None:
        #     pytest.skip("Invalid case.")

        ecl_keywords: list[str] = ["PRESSURE", "SGAS"]
        init_keywords: list[str] = ["PERMX"]
        summary_keywords: list[str] = ["WBHP:INJ0"]
        OPM: str = "/home/peter/Documents/2023_CEMRACS/opm"
        FLOW: str = f"{OPM}/build/opm-simulators/bin/flow"

        with patch("builtins.open", mock_open()):
            data = run_ensemble(
                FLOW,
                fixture_setup_ensemble,
                runspecs,
                ecl_keywords,
                init_keywords,
                summary_keywords,
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


# pylint: enable=unused-argument, invalid-name


@pytest.mark.parametrize("num_members", [1, 5, 10])
def test_memory_efficient_sample(num_members: int):
    # Create sample input data.
    num_samples = 100
    num_variables = 5
    variables = rng.random((num_variables, num_samples))

    # Call the function.
    result = memory_efficient_sample(variables, num_members)

    # Assert the result has the right shape.
    assert isinstance(result, np.ndarray)
    assert result.shape == (num_variables, num_members)

    # Assert the result has the right values.
    for i in range(num_variables):
        for member in result[i]:
            assert member in variables[i]


# TODO: Implement tests for the following functions.
# def test_extract_features():
#     pass

# def test_calculate_radii():
#     pass


@pytest.mark.parametrize(
    "pressures,injection_rates,expected_WI,expected_failed_indices",
    [
        (
            np.array([[100, 90, 80, 60]], dtype=np.float32),
            10.0,
            np.array([[1.0, 0.5, 0.25]]),
            [],
        ),
        (
            np.array([[100, 90, 80, 60], [110, 100, 90, 70]]),
            np.array([10.0, 20.0]),
            np.array([[1.0, 0.5, 0.25], [2.0, 1.0, 0.5]]),
            [],
        ),
        (
            np.array([[100, 90, 80, 60], [100, 100, 90, 80]]),
            np.array([10.0, 20.0]),
            np.array([[1.0, 0.5, 0.25]]),
            [1],
        ),
    ],
)
def test_calculate_WI(  # pylint: disable=invalid-name
    pressures: np.ndarray,
    injection_rates: np.ndarray,
    expected_WI: np.ndarray,  # pylint: disable=invalid-name
    expected_failed_indices: list[int],
):
    # pylint: disable-next=invalid-name
    WI_array, failed_indices = calculate_WI(pressures, injection_rates)
    assert np.allclose(WI_array, expected_WI)
    assert failed_indices == expected_failed_indices


@pytest.mark.parametrize(
    "radial_values, radii, block_sidelength, expected",
    [
        (
            np.array([2.0, 2.0, 2.0, 2.0]),
            np.array([0.0, 1.0, 2.0, 3.0, 4.0]),
            4.0,
            32.0,
        ),  # Expected result calculated by hand.
        (np.array([]), np.array([]), 4.0, 0.0),  # Empty data should result in 0.
    ],
)
def test_integrate_fine_scale_value(radial_values, radii, block_sidelength, expected):
    result = integrate_fine_scale_value(radial_values, radii, block_sidelength)
    assert pytest.approx(result, rel=1e-7) == expected


@pytest.mark.parametrize(
    "flags, expected_value",
    [
        ("flow --flag1 --flag2=value --flag3\n", "--flag1 --flag2=value --flag3"),
        ("${FLOW} --flag1=2 --flag3=test --flag", "--flag1=2 --flag3=test --flag"),
    ],
)
def test_get_flags(flags: str, expected_value: str, tmp_path):
    makofile = tmp_path / "test.mako"
    with makofile.open("w") as f:  # pylint: disable=invalid-name
        f.write("\n")
        f.write(flags)
    flags = get_flags(makofile)
    assert flags == expected_value
