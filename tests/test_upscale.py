# pylint: disable=missing-function-docstring, fixme
"""Tests for the ``pyopmnearwell.ml.upscale`` module.

Some of the test are not fixed yet. These get skipped.

"""

import math
import pathlib

import numpy as np
import pytest

from pyopmnearwell.ml.upscale import BaseUpscaler

rng: np.random.Generator = np.random.default_rng()

dirname: pathlib.Path = pathlib.Path(__file__).parent


# pylint: disable-next=missing-class-docstring
class MockUpscaler(BaseUpscaler):
    def __init__(self) -> None:
        self.num_timesteps = 10
        self.num_layers = 10
        self.num_zcells = 10
        self.num_xcells = 10
        self.single_feature_shape = (10, 10, 10, 10)
        self.angle = math.pi / 3

    def create_ds(self) -> None:
        return None


@pytest.fixture(name="test_upscaler")
def fixture_test_upscaler() -> MockUpscaler:
    return MockUpscaler()


@pytest.fixture(
    params=[
        rng.random((10, 20, 30, 40, 5)),
        rng.random((5, 1, 15, 20, 5)),
        rng.random((5, 10, 15, 1, 5)),
        rng.random((3, 1, 15, 1, 20)),
    ],
    name="feature",
)
def fixture_feature(request) -> np.ndarray:
    return request.param


@pytest.mark.parametrize("step_size_x", [2, 4, 8])
@pytest.mark.parametrize("step_size_t", [1, 2, 3])
def test_reduce_data_size(
    test_upscaler: MockUpscaler,
    feature: np.ndarray,
    step_size_x: int,
    step_size_t: int,
) -> None:
    feature_shape: list[int] = list(feature.shape)
    feature_shape[-2] = math.ceil(feature_shape[-2] / step_size_x)
    feature_shape[1] = math.ceil(feature_shape[1] / step_size_t)

    reduced_feature = test_upscaler.reduce_data_size(feature, step_size_x, step_size_t)

    assert reduced_feature.shape == tuple(feature_shape)


def test_get_vertically_averaged_values(test_upscaler: MockUpscaler) -> None:
    # TOOD: Fix this test.
    pytest.skip("Not implemented yet.")
    features: np.ndarray = rng.random((10, 20, 30, 40, 5))
    feature_index: int = 2
    averaged_values: np.ndarray = test_upscaler.get_vertically_averaged_values(
        features, feature_index
    )
    assert averaged_values.shape == (10, 20, 1, 40, 5)


def test_get_radii(test_upscaler: MockUpscaler) -> None:
    radii_file: pathlib.Path = dirname / "upscale" / "radii.txt"
    cell_center_radii, cell_boundary_radii = test_upscaler.get_radii(radii_file)
    assert cell_center_radii.shape == (test_upscaler.num_xcells,)
    assert cell_boundary_radii.shape == (test_upscaler.num_xcells + 1,)


# TODO: Implement this test.
def test_create_ds() -> None:
    pass


def test_get_timesteps(test_upscaler) -> None:
    # TOOD: Fix this test.
    pytest.skip("Not implemented yet.")
    simulation_length: float = 10.0
    timesteps: np.ndarray = test_upscaler.get_timesteps(simulation_length)
    assert len(timesteps) == test_upscaler.num_timesteps
    assert timesteps[-1] == simulation_length


def test_get_horizontically_integrated_values(test_upscaler: MockUpscaler) -> None:
    # TOOD: Fix this test.
    pytest.skip("Not implemented yet.")
    features = rng.random((10, 20, 30, 40, 5))
    radii_file: pathlib.Path = pathlib.Path("path/to/radii_file.txt")
    cell_center_radii, cell_boundary_radii = test_upscaler.get_radii(radii_file)
    feature_index: int = 2
    integrated_values = test_upscaler.get_horizontically_integrated_values(
        features, cell_center_radii, cell_boundary_radii, feature_index
    )
    assert integrated_values.shape == (10, 20, 30, 1)


def test_get_homogeneous_values(test_upscaler: MockUpscaler) -> None:
    # TOOD: Fix this test.
    pytest.skip("Not implemented yet.")
    features: np.ndarray = rng.random((10, 20, 30, 40, 5))
    feature_index: int = 2
    homogeneous_values = test_upscaler.get_homogeneous_values(features, feature_index)
    assert homogeneous_values.shape == (10, 20, 30, 1)


# pylint: disable-next=invalid-name
def test_get_analytical_WI(test_upscaler: MockUpscaler) -> None:
    # TOOD: Fix this test.
    pytest.skip("Not implemented yet.")
    pressures: np.ndarray = rng.random((10, 20, 30, 40))
    saturations: np.ndarray = rng.random((10, 20, 30, 40))
    permeabilities: np.ndarray = rng.random((10, 20, 30, 40))
    temperature: float = 300.0
    surface_density: float = 0.1
    radii: np.ndarray = rng.random((40))
    OPM: pathlib.Path = pathlib.Path("path/to/OPM.txt")  # pylint: disable=invalid-name
    analytical_WI = test_upscaler.get_analytical_WI(  # pylint: disable=invalid-name
        pressures,
        saturations,
        permeabilities,
        temperature,
        surface_density,
        radii,
        well_radius=0.1,
        OPM=OPM,
    )
    assert analytical_WI.shape == (10, 20, 30, 40)


# pylint: disable-next=invalid-name
def test_get_data_WI(test_upscaler: MockUpscaler) -> None:
    # TOOD: Fix this test.
    pytest.skip("Not implemented yet.")
    features: np.ndarray = rng.random((10, 20, 30, 40, 5))
    # pressures = rng.random((10, 20, 30, 40))
    pressure_index: int = 2
    inj_rate_index: int = 3
    angle: float = math.pi / 3
    # pylint: disable-next=invalid-name
    data_WI: np.ndarray = test_upscaler.get_data_WI(
        features, pressure_index, inj_rate_index, angle
    )
    assert data_WI.shape == (10, 20, 30, 40)
