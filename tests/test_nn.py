import csv
import os

import numpy as np
import pytest
import tensorflow as tf
from tensorflow import keras

from pyopmnearwell.ml.nn import scale_and_evaluate


@pytest.fixture
def identity_nn() -> keras.Model:
    model: keras.Model = keras.Sequential([keras.layers.Identity()])
    return model


@pytest.fixture(params=[[[1, 2]], [[3.2, -5.8]], [[-12.3, 14.58]], [[-5, -20.5]]])
def feature_batch(request) -> np.ndarray:
    return np.array(request.param)


@pytest.fixture(
    params=[
        {
            "v_0": (0.0, 100.0),
            "v_1": (-5.0, 5.0),
            "WI_1": (5.0, 10.0),
            "WI_2": (-20.0, -10.0),
            "feature_range": (-1.0, 1.0),
            "target_range": (-5.0, 1.0),
        },
        {
            "v_0": (-3.5, 20.5),
            "v_1": (-7.4, -5.6),
            "WI_1": (-400, 30.0),
            "WI_2": (375.5, 380.92),
            "feature_range": (0.0, 1.0),
            "target_range": (5.0, 10.0),
        },
        {
            "v_0": (20, 20.5),
            "v_1": (-14, -13),
            "WI_1": (-40559.5, 1.0),
            "WI_2": (-600.5, 2292),
        },
    ]
)
def scalings(request) -> dict[str, tuple[float, float]]:
    return request.param


@pytest.fixture
def write_scalings(
    scalings: dict[str, tuple[float, float]],
    tmp_path_factory,
) -> str:
    dirname = tmp_path_factory.mktemp("test_nn")
    with open(os.path.join(dirname, "scalings.csv"), "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["variable", "min", "max"])
        writer.writeheader()
        for variable_name, (variable_min, variable_max) in scalings.items():
            writer.writerow(
                {"variable": variable_name, "min": variable_min, "max": variable_max}
            )
    return dirname


def test_scale_and_evaluate(
    identity_nn: keras.Model,
    feature_batch: tf.Tensor,
    scalings: dict[str, tuple[float, float]],
    write_scalings: str,
) -> None:
    """Test that the function ``ml.nn.scale_and_evaluate`` returns the correct result.

    Args:
        identity_nn (keras.Model): _description_
        feature_batch (tf.Tensor): _description_
        scalings (dict[str, tuple[float, float]]): _description_
        write_scalings (None): _description_
        temp_ensemble_dir (str): _description_
    """
    output_batch = scale_and_evaluate(
        identity_nn, feature_batch, os.path.join(write_scalings, "scalings.csv")
    )
    feature_scalings: list[tuple[float, float]] = list(scalings.values())[:2]
    output_scalings: list[tuple[float, float]] = list(scalings.values())[2:4]
    if len(list(scalings.values())) > 4:
        feature_range: tuple[float, float] = list(scalings.values())[4]
        target_range: tuple[float, float] = list(scalings.values())[5]
    else:
        feature_range = (-1, 1)
        target_range = (-1, 1)
    for i, (feature_min, feature_max), (target_min, target_max) in zip(
        range(output_batch.shape[-1]), feature_scalings, output_scalings
    ):
        std_feature: np.ndarray = (feature_batch[..., i] - feature_min) / (
            feature_max - feature_min
        )
        scaled_feature: np.ndarray = (
            std_feature * (feature_range[1] - feature_range[0]) + feature_range[0]
        )
        # The nn consists of one identity layer, hence the features and outputs are
        # identical.
        scaled_output: np.ndarray = scaled_feature
        std_output: np.ndarray = (scaled_output - target_range[0]) / (
            target_range[1] - target_range[0]
        )
        unscaled_output: np.ndarray = (
            std_feature * (target_max - target_min)
        ) + target_min

        assert pytest.approx(output_batch[..., i], rel=1e-4) == unscaled_output


def test_scale_and_prepare_dataset() -> None:
    pass
