# pylint: skip-file
from __future__ import annotations

import pathlib

import numpy as np
from tensorflow import keras

from pyopmnearwell.ml.kerasify import export_model
from pyopmnearwell.ml.scaler_layers import MinMaxScalerLayer, MinMaxUnScalerLayer

savepath = pathlib.Path(__file__).parent / "model_with_scaler_layers.opm"

feature_ranges: list[tuple[float, float]] = [(0.0, 1.0), (-3.7, 0.0)]
data: np.ndarray = np.random.uniform(-500, 500, (5, 1))

model: keras.Model = keras.Sequential(
    [
        keras.layers.Input([10]),
        MinMaxScalerLayer(feature_range=feature_ranges[0]),
        keras.layers.Dense(units=10),
        MinMaxUnScalerLayer(feature_range=feature_ranges[1]),
    ]
)
model.get_layer(model.layers[0].name).adapt(data=data)
model.get_layer(model.layers[-1].name).adapt(data=data)

export_model(model, str(savepath))
