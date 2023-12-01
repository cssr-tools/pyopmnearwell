import math
from pathlib import Path

import numpy as np
import pytest

from pyopmnearwell.ml.data import BaseDataset


@pytest.fixture
def base_dataset():
    return BaseDataset()


@pytest.fixture(
    params=[
        np.random.rand(10, 20, 30, 40, 5),
        np.random.rand(5, 1, 15, 20, 5),
        np.random.rand(5, 10, 15, 1, 5),
        np.random.rand(3, 1, 15, 1, 20),
    ]
)
def feature(request) -> np.ndarray:
    return request.param


@pytest.mark.parametrize("step_size_x", [2, 4, 8])
@pytest.mark.parametrize("step_size_t", [1, 2, 3])
def test_reduce_data_size(
    base_dataset: BaseDataset,
    feature: np.ndarray,
    step_size_x: int,
    step_size_t: int,
):
    feature_shape: list[int] = list(feature.shape)
    feature_shape[-1] = math.floor(feature_shape[-1] / step_size_x)
    feature_shape[1] = math.floor(feature_shape[1] / step_size_t)

    reduced_feature = base_dataset.reduce_data_size(feature, step_size_x, step_size_t)

    assert reduced_feature.shape == tuple(feature_shape)


def test_get_vertically_averaged_values(base_dataset: BaseDataset):
    features = np.random.rand(10, 20, 30, 40, 5)
    feature_index = 2
    averaged_values = base_dataset.get_vertically_averaged_values(
        features, feature_index
    )
    assert averaged_values.shape == (10, 20, 30, 40)


def test_get_radii(base_dataset: BaseDataset):
    radii_file = Path("path/to/radii_file.txt")
    cell_center_radii, cell_boundary_radii = base_dataset.get_radii(radii_file)
    assert cell_center_radii.shape == (40,)
    assert cell_boundary_radii.shape == (41,)


def test_create_ds(base_dataset: BaseDataset):
    pass


def test_get_timesteps(base_dataset):
    simulation_length = 10.0
    timesteps = base_dataset.get_timesteps(simulation_length)
    assert len(timesteps) == base_dataset.num_timesteps
    assert timesteps[-1] == simulation_length


def test_get_horizontically_integrated_values(base_dataset: BaseDataset):
    features = np.random.rand(10, 20, 30, 40, 5)
    radii_file = Path("path/to/radii_file.txt")
    cell_center_radii, cell_boundary_radii = base_dataset.get_radii(radii_file)
    feature_index = 2
    integrated_values = base_dataset.get_horizontically_integrated_values(
        features, cell_center_radii, cell_boundary_radii, feature_index
    )
    assert integrated_values.shape == (10, 20, 30, 1)


def test_get_homogeneous_values(base_dataset: BaseDataset):
    features = np.random.rand(10, 20, 30, 40, 5)
    feature_index = 2
    homogeneous_values = base_dataset.get_homogeneous_values(features, feature_index)
    assert homogeneous_values.shape == (10, 20, 30, 1)


def test_get_analytical_WI(base_dataset: BaseDataset):
    pressures = np.random.rand(10, 20, 30, 40)
    saturations = np.random.rand(10, 20, 30, 40)
    permeabilities = np.random.rand(10, 20, 30, 40)
    temperature = 300.0
    surface_density = 0.1
    radii = np.random.rand(40)
    OPM = Path("path/to/OPM.txt")
    analytical_WI = base_dataset.get_analytical_WI(
        pressures,
        saturations,
        permeabilities,
        temperature,
        surface_density,
        radii,
        OPM,
    )
    assert analytical_WI.shape == (10, 20, 30, 40)


def test_get_data_WI(base_dataset: BaseDataset):
    features = np.random.rand(10, 20, 30, 40, 5)
    pressures = np.random.rand(10, 20, 30, 40)
    pressure_index = 2
    inj_rate_index = 3
    angle = math.pi / 3
    data_WI = base_dataset.get_data_WI(
        features, pressures, pressure_index, inj_rate_index, angle
    )
    assert data_WI.shape == (10, 20, 30, 40)
