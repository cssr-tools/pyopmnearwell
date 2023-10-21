# """Provide MinMax scaler layers for tensorflow.keras"""
from __future__ import annotations

from typing import Any, Optional

import numpy as np
import tensorflow as tf
from numpy.typing import ArrayLike
from tensorflow import keras
from tensorflow import python as tf_python  # pylint: disable=E0611


class ScalerLayer(keras.layers.Layer):
    """MixIn to provide functionality for the Scaler Layer."""

    data_min: tf.Tensor
    data_max: tf.Tensor

    def __init__(
        self,
        # TODO: Is float a subset of
        data_min: Optional[float | ArrayLike] = None,
        data_max: Optional[float | ArrayLike] = None,
        feature_range: ArrayLike = tf.Tensor([0, 1]),
        **kwargs,  # pylint: disable=W0613
    ) -> None:
        super().__init__()
        self.feature_range: tf.Tensor = tf.convert_to_tensor(feature_range)
        self._is_adapted: bool = False
        if data_min is not None and data_max is not None:
            self.data_min = tf.convert_to_tensor(data_min)
            self.data_max = tf.convert_to_tensor(data_max)
            self._adapt()

    def build(self, input_shape: tuple[int, ...]) -> None:
        """Initialize ``data_min`` and ``data_max`` with the default values if they have
        not been initialized yet.

        Args:
            input_shape (tuple[int, ...]): _description_

        """
        if not self._is_adapted:
            # ``data_min`` and ``data_max`` have the same shape as one input tensor.
            self.data_min = tf.zeros(input_shape[1:])
            self.data_max = tf.ones(input_shape[1:])
            self._adapt()

    def get_weights(self) -> list[ArrayLike]:
        return [self.data_min, self.data_max, self.feature_range]

    def set_weights(self, weights: list[np.ndarray]) -> None:
        self.data_min = weights[0]
        self.data_max = weights[1]
        self.feature_range = weights[2]

    # TODO
    # Implement only if something special needs to be saved in the config compared to the base layer.
    # Every element of the config needs to be serialized.

    # Ignore pylint complaining about a missing docstring.
    def get_config(self) -> dict[str, Any]:  # pylint: disable=C0116
        config = super().get_config()  # type: ignore # pylint: disable=E1101
        # Note: This returns the dict, but raises a warning that the layers is not JSON
        # serializable. Fix this!
        config.update(
            {
                "feature_range": self.feature_range,
                "data_max": self.data_max,
                "data_min": self.data_min,
            }
        )
        return config

    def from_config(self, config: dict[str, Any]) -> None:
        pass

    def adapt(self, data: ArrayLike) -> None:
        """Fit the layer to the min and max of the data. This is done individually for
        each input feature.

        Note:
            So far, this is only tested for 1 dimensional input and output. For higher
            dimensional input and output some functionality might need to be added.

        Args:
            data: _description_

        """
        data = tf.convert_to_tensor(data)
        self.data_min = tf.math.reduce_min(data, axis=0)
        self.data_max = tf.math.reduce_max(data, axis=0)
        self._adapt()

    def _adapt(self) -> None:
        if tf.math.reduce_any(self.data_min > self.data_max):
            raise RuntimeError(
                f"""self.data_min {self.data_min} cannot be larger than self.data_max
                {self.data_max} for any element."""
            )
        self.scalar = tf.where(
            self.data_max > self.data_min,
            self.data_max - self.data_min,
            tf.ones_like(self.data_min),
        )
        self.min = tf.where(
            self.data_max > self.data_min,
            self.data_min,
            tf.zeros_like(self.data_min),
        )
        self._is_adapted = True


class MinMaxScalerLayer(
    ScalerLayer, tf_python.keras.engine.base_preprocessing_layer.PreprocessingLayer
):
    """Scales the input according to MinMaxScaling.

    See
    https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
    for an explanation of the transform.

    """

    def __init__(
        self,
        data_min: Optional[float | ArrayLike] = None,
        data_max: Optional[float | ArrayLike] = None,
        feature_range: ArrayLike = tf.Tensor([0, 1]),
        **kwargs,  # pylint: disable=W0613
    ) -> None:
        super().__init__(data_min, data_max, feature_range, **kwargs)
        self._name: str = "MinMaxScalerLayer"

    # Ignore pylint complaining about a missing docstring.
    def call(self, inputs: tf.Tensor) -> tf.Tensor:  # pylint: disable=C0116
        if not self.is_adapted:
            print(np.greater_equal(self.data_min, self.data_max))
            raise RuntimeError(
                """The layer has not been adapted correctly. Call ``adapt`` before using
                the layer or set the ``data_min`` and ``data_max`` values manually.
                """
            )

        # TODO: Does this conversion to tensors need to be done?
        inputs = tf.convert_to_tensor(inputs)
        scaled_data = (inputs - self.min) / self.scalar
        return self.feature_range[0] + (
            scaled_data * (self.feature_range[1] - self.feature_range[0])
        )


class MinMaxUnScalerLayer(ScalerLayer, tf.keras.layers.Layer):
    """Unscales the input by applying the inverse transform of ``MinMaxScalerLayer``.

    See
    https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.MinMaxScaler.html
    for an explanation of the transform.

    """

    def __init__(
        self,
        data_min: Optional[float | ArrayLike] = None,
        data_max: Optional[float | ArrayLike] = None,
        feature_range: ArrayLike = np.array([0, 1]),
        **kwargs,  # pylint: disable=W0613
    ) -> None:
        super().__init__(data_min, data_max, feature_range, **kwargs)
        self._name: str = "MinMaxUnScalerLayer"

    # Ignore pylint complaining about a missing docstring and something else.
    def call(self, inputs: tf.Tensor) -> tf.Tensor:  # pylint: disable=W0221
        if not self._is_adapted:
            raise RuntimeError(
                """The layer has not been adapted correctly. Call ``adapt`` before using
                the layer or set the ``data_min`` and ``data_max`` values manually."""
            )

        # TODO: Does this conversion to tensors need to be done?
        inputs = tf.convert_to_tensor(inputs)
        unscaled_data = inputs * self.scalar + self.min
        return unscaled_data
