# pylint: skip-file
# pylint: disable=missing-function-docstring
"""Test the ``ml.scaler_layers`` module.

Warning: Tensorflow 2.17 and Keras 3.0 make all tests fail, hence we disable them
completely. It is possible that the ``scalar_layers`` module is not functional at the
moment.
"""

from __future__ import annotations

import itertools
import pathlib

import keras
import numpy as np
import pytest
from sklearn.preprocessing import MinMaxScaler

from pyopmnearwell.ml.scaler_layers import MinMaxScalerLayer, MinMaxUnScalerLayer

rng: np.random.Generator = np.random.default_rng()

layers: list[str] = ["scaler", "unscaler"]
feature_ranges: list[tuple[float, float]] = [(0.0, 1.0), (-3.7, 0.0), (-5.0, 4.0)]


@pytest.fixture(
    params=itertools.product(layers, feature_ranges), name="layers_and_feature_ranges"
)
def fixture_layers_and_feature_ranges(request) -> tuple[str, tuple[float, float]]:
    return request.param


@pytest.fixture(
    params=[rng.uniform(-500, 500, (5, 1)) for _ in range(5)],
    name="data",
)
def fixture_data(request) -> np.ndarray:
    return request.param


@pytest.fixture(name="fitted_model")
def fixture_fitted_model(
    layers_and_feature_ranges: tuple[str, tuple[float, float]], data: np.ndarray
) -> keras.Model:
    layer: str = layers_and_feature_ranges[0]
    # pylint: disable=redefined-outer-name
    feature_ranges: tuple[float, float] = layers_and_feature_ranges[1]
    if layer == "scaler":
        scalerlayer = MinMaxScalerLayer(feature_range=feature_ranges)

    elif layer == "unscaler":
        scalerlayer = MinMaxUnScalerLayer(feature_range=feature_ranges)

    # pylint: disable-next=possibly-used-before-assignment
    scalerlayer.adapt(data=data)  # type: ignore

    model = keras.Sequential(
        [
            keras.layers.Input([1]),
            scalerlayer,
        ]
    )
    return model


@pytest.fixture(name="fitted_scaler")
def fixture_fitted_scaler(
    layers_and_feature_ranges: tuple[str, tuple[float, float]], data: np.ndarray
) -> MinMaxScaler:
    scaler: MinMaxScaler = MinMaxScaler(feature_range=layers_and_feature_ranges[1])  # type: ignore
    scaler.fit(data)
    return scaler


def test_save_scaler_layer(fitted_model: keras.Model, tmp_path: pathlib.Path) -> None:
    fitted_model.save(tmp_path / "model.keras")
    assert (tmp_path / "model.keras").exists()

    # Load the saved model
    loaded_model: keras.Model = keras.models.load_model(  # type: ignore
        tmp_path / "model.keras",
        compile=False,
        custom_objects={
            "MinMaxUnScalerLayer": MinMaxUnScalerLayer,
            "MinMaxScalerLayer": MinMaxScalerLayer,
        },
    )

    # Check if both model have the same is_adapted state
    assert fitted_model.layers[0].is_adapted == loaded_model.layers[0].is_adapted

    # Check if all parameters from ScalerLayer layer are equal for both models
    data_min1, data_max1, feature_ranges1 = fitted_model.layers[0].get_weights()
    data_min2, data_max2, feature_ranges2 = loaded_model.layers[0].get_weights()

    assert np.array(data_min1[0]) == np.array(data_min2[0])
    assert np.array(data_max1[0]) == np.array(data_max2[0])
    assert np.array_equal(feature_ranges1, feature_ranges2)


@pytest.mark.parametrize(
    "model_input",
    [rng.uniform(-500, 500, (5, 1)) for _ in range(5)],
)
def test_minmax_scaler_layer(
    model_input: np.ndarray,
    fitted_model: keras.Model,
    fitted_scaler: MinMaxScaler,
) -> None:

    scaled: np.ndarray = fitted_model(model_input)
    if fitted_model.layers[0].name == "MinMaxScalerLayer":
        assert np.allclose(scaled, fitted_scaler.transform(model_input), rtol=1e-3)
    elif fitted_model.layers[0].name == "MinMaxUnScalerLayer":
        assert np.allclose(
            scaled, fitted_scaler.inverse_transform(model_input), rtol=1e-3
        )


@pytest.mark.parametrize("input_shape", [(1, 10), (2, 20), (10, 15)])
def test_minmaxscaler_with_multiple_features_and_samples(input_shape):
    data = [rng.uniform(-500, 500, input_shape)]

    scalerlayer = MinMaxScalerLayer()
    unscalerlayer = MinMaxUnScalerLayer()

    scalerlayer.adapt(data)
    unscalerlayer.adapt(data)

    model = keras.Sequential(
        [keras.layers.Input([input_shape[1]]), scalerlayer, unscalerlayer]
    )

    pred = model(data)
    # Check if model is identity
    assert np.allclose(pred, data, rtol=1e-3)
    # Check if all features have their own min and max.
    # Data is shape (Ndata, Nfeatures) and min is shape (1, Nfeatures)
    assert scalerlayer.data_min.shape[1] == input_shape[1]
    assert scalerlayer.data_max.shape[1] == input_shape[1]


@pytest.mark.parametrize(
    "feature_range",
    [[(0.0, 1.0), (2.0, 3.0), (4.0, 5.0)], [(-1.0, 0.0), (-2.0, 0)], [(0.0, 1.0)]],
)
def test_minmaxscaler_with_multiple_features_ranges(feature_range):
    data = [rng.uniform(-500, 500, (10, len(feature_range)))]

    scalerlayer = MinMaxScalerLayer(feature_range=feature_range)
    unscalerlayer = MinMaxUnScalerLayer(feature_range=feature_range)

    scalerlayer.adapt(data)
    unscalerlayer.adapt(data)

    model = keras.Sequential(
        [keras.layers.Input([len(feature_range)]), scalerlayer, unscalerlayer]
    )

    pred = model(data)
    # Check if model is identity
    assert np.allclose(pred, data, rtol=1e-3)

    # Check that feature_ranges have correct shape
    assert len(scalerlayer.feature_range) == len(feature_range)
    for fr1, fr2 in zip(scalerlayer.feature_range, feature_range):
        assert fr1[0] == fr2[0] and fr1[1] == fr2[1]
