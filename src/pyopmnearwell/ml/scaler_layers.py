"""Provide MinMax scaler layers for tensorflow.keras"""
from __future__ import annotations

from typing import Optional

import numpy as np
import tensorflow as tf
from tensorflow import python as tf_python  # pylint: disable=E0611


class ScalerLayer:
    """MixIn to provide functionality for the Scaler Layer."""

    def __init__(
        self,
        data_min: Optional[float | np.ndarray] = None,
        data_max: Optional[float | np.ndarray] = None,
        feature_range: tuple[float, float] = (0, 1),
        **kwargs,  # pylint: disable=W0613
    ):
        super().__init__()
        self.feature_range = feature_range
        if data_min is not None and data_max is not None:
            self.data_min = data_min
            self.data_max = data_max
            self._adapt()

    def adapt(self, data):
        """Fit the layer to the min and max of the data. This is done individually for
        each input feature.

        Parameters:
            data: _description_
        """
        data = tf.convert_to_tensor(data)
        self.data_min = tf.math.reduce_min(data, axis=0)
        self.data_max = tf.math.reduce_max(data, axis=0)
        self._adapt()

    def _adapt(self):
        if np.any(self.data_min > self.data_max):
            raise RuntimeError(
                f"""self.data_min {self.data_min} cannot be larger than self.data_max
                {self.data_max} for any element"""
            )
        self.scalar = np.where(
            self.data_max > self.data_min,
            self.data_max - self.data_min,
            np.ones_like(self.data_min),
        )
        self.min = np.where(
            self.data_max > self.data_min,
            self.data_min,
            np.zeros_like(self.data_min),
        )
        self._is_adapted = True

    # Ignore pylint complaining about a missing docstring.
    def set_params(self, params: dict[str, float]):  # pylint: disable=C0116
        for key, value in params.items():
            try:
                setattr(self, key, value)
            except KeyError:
                raise KeyError(  # pylint: disable=W0707
                    "Please pass a valid parameter."
                )

    # Ignore pylint complaining about a missing docstring.
    def get_config(self):  # pylint: disable=C0116
        config = super().get_config()  # pylint: disable=E1101
        config.update(
            {
                "feature_range": self.feature_range,
                "data_max": self.data_max,
                "data_min": self.data_min,
            }
        )
        return config


class MinMaxScalerLayer(
    ScalerLayer, tf_python.keras.engine.base_preprocessing_layer.PreprocessingLayer
):
    """Scales the input according to MinMaxScaling.

    See
    https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
    for an explanation of the transform.

    """

    # Ignore pylint complaining about a missing docstring.
    def call(self, inputs):  # pylint: disable=C0116
        if not self.is_adapted:
            print(np.greater_equal(self.data_min, self.data_max))
            raise RuntimeError(
                """The layer has not been adapted correctly. Call ``adapt`` before using
                the layer or set the ``data_min`` and ``data_max`` values manually."""
            )

        inputs = tf.convert_to_tensor(inputs)
        scaled_data = (inputs - self.min) / self.scalar
        # return self.feature_range[0] + (
        #     scaled_data * (self.feature_range[1] - self.feature_range[0])
        # )
        return scaled_data


class MinMaxUNScalerLayer(ScalerLayer, tf.keras.layers.Layer):
    """Unscales the input by applying the inverse transform of ``MinMaxScalerLayer``.

    See
    https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
    for an explanation of the transform.

    """

    # Ignore pylint complaining about a missing docstring and something else.
    def call(self, inputs):  # pylint: disable=W0221
        if not self._is_adapted:
            raise RuntimeError(
                """The layer has not been adapted correctly. Call ``adapt`` before using
                the layer or set the ``data_min`` and ``data_max`` values manually."""
            )

        inputs = tf.convert_to_tensor(inputs)
        unscaled_data = inputs * self.scalar + self.min
        return unscaled_data
