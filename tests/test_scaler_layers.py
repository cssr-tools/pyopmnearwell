"""Test the ``ml.scaler_layers`` module."""
import itertools
import os

import numpy as np
import pytest
from tensorflow import keras

from pyopmnearwell.ml.scaler_layers import (
    MinMaxScalerLayer,
    MinMaxUnScalerLayer,
    ScalerLayer,
)

layers: list[str] = ["scaler", "unscaler"]
feature_ranges: list[tuple[int, int]] = [(0, 1), (-1, 0), (-5, 4)]


@pytest.fixture(params=itertools.product(layers, feature_ranges))
def model(request) -> keras.Model:
    if request.param[0] == "scaler":
        return keras.Sequential(
            [
                keras.layers.Input([10]),
                MinMaxScalerLayer(feature_range=request.param[1]),
            ]
        )
    elif request.param[0] == "unscaler":
        return keras.Sequential([MinMaxUnScalerLayer(feature_range=request.param[1])])


@pytest.fixture(
    params=[np.random.uniform(-500, 500, (5, 1)) for _ in range(5)]
    + [np.random.uniform(-500, 500, (5, 10)) for _ in range(5)]
)
def fit_model(request, model: keras.Model) -> keras.Model:
    model.get_layer(model.layers[0].name).adapt(data=request.param)
    return model


def test_scaler_model(fit_model: keras.Model, tmp_path: str) -> None:
    fit_model.save(os.path.join(tmp_path, "model.pb"))
    assert os.path.exists(os.path.join(tmp_path, "model.pb"))
    # TODO: test that the model gets load correctly.
