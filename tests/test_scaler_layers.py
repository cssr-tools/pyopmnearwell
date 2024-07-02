# pylint: disable=missing-function-docstring
"""Test the ``ml.scaler_layers`` module."""

from __future__ import annotations

import itertools
import pathlib

import numpy as np
import pytest
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras

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
    params=[rng.uniform(-500, 500, (5, 1)) for _ in range(5)]
    + [rng.uniform(-500, 500, (5, 10)) for _ in range(5)],
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
        model: keras.Model = keras.Sequential(
            [
                keras.layers.Input([10]),
                MinMaxScalerLayer(feature_range=feature_ranges),
            ]
        )
    elif layer == "unscaler":
        model = keras.Sequential(
            [
                keras.layers.Input([10]),
                MinMaxUnScalerLayer(feature_range=feature_ranges),
            ]
        )

    # pylint: disable-next=possibly-used-before-assignment
    model.get_layer(model.layers[0].name).adapt(data=data)  # type: ignore
    return model


@pytest.fixture(name="fitted_scaler")
def fixture_fitted_scaler(
    layers_and_feature_ranges: tuple[str, tuple[float, float]], data: np.ndarray
) -> MinMaxScaler:
    scaler: MinMaxScaler = MinMaxScaler(feature_range=layers_and_feature_ranges[1])  # type: ignore
    scaler.fit(data)
    return scaler


def test_save_scaler_layer(fitted_model: keras.Model, tmp_path: pathlib.Path) -> None:
    fitted_model.save(tmp_path / "model.pb")
    assert (tmp_path / "model.pb").exists()

    # Load the saved model
    loaded_model: keras.Model = keras.models.load_model(  # type: ignore
        tmp_path / "model.pb", compile=False
    )

    # Check if all parameters are equal for both models
    for weight1, weight2 in zip(
        fitted_model.layers[0].get_weights(), loaded_model.layers[0].get_weights()
    ):
        assert np.array_equal(weight1, weight2)


@pytest.mark.parametrize(
    "model_input",
    [rng.uniform(-500, 500, (5, 1)) for _ in range(5)]
    + [rng.uniform(-500, 500, (5, 10)) for _ in range(5)],
)
def test_minmax_scaler_layer(
    model_input: np.ndarray,
    fitted_model: keras.Model,
    fitted_scaler: MinMaxScaler,
) -> None:
    # Skip tests if the input data has different shape than the fitted model/scaler.
    if model_input.shape[1] != fitted_model.layers[0].get_weights()[0].shape[0]:
        pytest.skip()
    scaled: np.ndarray = fitted_model(model_input)
    if fitted_model.layers[0].name == "MinMaxScalerLayer":
        assert np.allclose(scaled, fitted_scaler.transform(model_input), rtol=1e-3)
    elif fitted_model.layers[0].name == "MinMaxUnScalerLayer":
        assert np.allclose(
            scaled, fitted_scaler.inverse_transform(model_input), rtol=1e-3
        )
