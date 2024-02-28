# pylint: disable=missing-function-docstring,fixme
"""Tests for the ``pyopmnearwell.ml.nn`` module."""
from __future__ import annotations

import csv
import pathlib
from typing import Literal

import numpy as np
import pytest
import tensorflow as tf
from numpy.testing import assert_allclose, assert_raises
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras

from pyopmnearwell.ml.ensemble import store_dataset
from pyopmnearwell.ml.nn import scale_and_evaluate, scale_and_prepare_dataset

rng: np.random.Generator = np.random.default_rng()


@pytest.fixture(name="identity_nn")
def fixture_identity_nn() -> keras.Model:
    model: keras.Model = keras.Sequential([keras.layers.Identity()])
    return model


@pytest.fixture(
    params=[[[1, 2]], [[3.2, -5.8]], [[-12.3, 14.58]], [[-5, -20.5]]],
    name="feature_batch",
)
def fixture_feature_batch(request) -> np.ndarray:
    return np.array(request.param)


@pytest.fixture(
    params=[
        {
            "input_0": (0.0, 100.0),
            "input_1": (-5.0, 5.0),
            "output_1": (5.0, 10.0),
            "output_2": (-20.0, -10.0),
            "feature_range": (-1.0, 1.0),
            "target_range": (-5.0, 1.0),
        },
        {
            "input_0": (-3.5, 20.5),
            "input_1": (-7.4, -5.6),
            "output_1": (-400, 30.0),
            "output_2": (375.5, 380.92),
            "feature_range": (0.0, 1.0),
            "target_range": (5.0, 10.0),
        },
        {
            "input_0": (45, 220.5),
            "output_0": (-40559.5, 1.0),
            "target_range": (100.0, 110.0),
        },
        {
            "input_0": (20, 20.5),
            "input_1": (-14, -13),
            "output_1": (-40559.5, 1.0),
            "output_2": (-600.5, 2292),
        },
    ],
    name="scalings",
)
def fixture_scalings(request) -> dict[str, tuple[float, float]]:
    return request.param


@pytest.fixture(name="write_scalings")
def fixture_write_scalings(
    scalings: dict[str, tuple[float, float]],
    tmp_path_factory,
) -> pathlib.Path:
    dirname: pathlib.Path = tmp_path_factory.mktemp("test_nn")
    with (dirname / "scalings.csv").open("w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["variable", "min", "max"])
        writer.writeheader()
        for variable_name, (variable_min, variable_max) in scalings.items():
            writer.writerow(
                {"variable": variable_name, "min": variable_min, "max": variable_max}
            )
    return dirname


# TODO: Add tests with multidimensional input and output.
# pylint: disable-next=too-many-locals
def test_scale_and_evaluate(
    identity_nn: keras.Model,
    feature_batch: tf.Tensor,
    scalings: dict[str, tuple[float, float]],
    write_scalings: pathlib.Path,
) -> None:
    output_batch = scale_and_evaluate(
        identity_nn, feature_batch, write_scalings / "scalings.csv"
    )

    feature_scalings: list[tuple[float, float]] = [
        item for key, item in scalings.items() if key.startswith("input")
    ]
    output_scalings: list[tuple[float, float]] = [
        item for key, item in scalings.items() if key.startswith("output")
    ]
    feature_range: tuple[float, float] = scalings.get("feature_range", (-1, 1))
    target_range: tuple[float, float] = scalings.get("target_range", (-1, 1))

    for i, (feature_min, feature_max), (target_min, target_max) in zip(
        range(output_batch.shape[-1]), feature_scalings, output_scalings  # type: ignore
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
            std_output * (target_max - target_min)
        ) + target_min

        assert_allclose(output_batch[..., i], unscaled_output, rtol=1e-4)


@pytest.fixture(params=[1, 5, 20], name="feature_names")
def fixture_feature_names(request) -> list[str]:
    return [f"feat_{i}" for i in range(request.param)]


@pytest.fixture(params=[100, 1000], name="data")
def fixture_data(request, feature_names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    """Create data with sorted targets. This allows for comparing the different shuffle
    options."""
    features: np.ndarray = rng.random((request.param, len(feature_names)))
    targets: np.ndarray = np.sort(rng.random((request.param, 1)), axis=0)
    return features, targets


@pytest.fixture(name="dataset")
def fixture_dataset(
    data: tuple[np.ndarray, np.ndarray], tmp_path: pathlib.Path
) -> pathlib.Path:
    features, targets = data
    return store_dataset(features, targets, tmp_path / "dataset")


@pytest.fixture(name="target_scaler")
def fixture_target_scaler(data: tuple[np.ndarray, np.ndarray]) -> MinMaxScaler:
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(data[1])
    return scaler


# TODO: Add tests with multidimensional input and output. Make sure this works correctly
# with all shuffling.
@pytest.mark.parametrize("shuffle", ["first", "last", "false"])
# pylint: disable-next=too-many-locals,too-many-statements
def test_scale_and_prepare_dataset(
    shuffle: Literal["first", "last", "false"],
    dataset: pathlib.Path,
    feature_names: list[str],
    target_scaler: MinMaxScaler,
) -> None:
    """Test scale_and_prepare_dataset with different shuffle options."""
    scalings_path: pathlib.Path = dataset / ".." / "scalings"
    scalings_path.mkdir()

    # Ignore mypy complaining about the wrong number of values to unpack.
    train, val, test = scale_and_prepare_dataset(  # type: ignore
        dataset,
        feature_names,
        scalings_path,
        train_split=0.7,
        val_split=0.2,
        test_split=0.1,
        shuffle=shuffle,
        feature_range=(0, 1),
        target_range=(0, 1),
        scale=True,
    )

    orig_dataset: tf.data.Dataset = tf.data.Dataset.load(str(dataset))
    orig_train: tf.data.Dataset = orig_dataset.take(int(0.7 * len(orig_dataset)))
    orig_val: tf.data.Dataset = orig_dataset.skip(int(0.7 * len(orig_dataset))).take(
        int(0.2 * len(orig_dataset))
    )
    orig_test: tf.data.Dataset = orig_dataset.skip(int(0.9 * len(orig_dataset)))

    # Check that the splits add up to the correct size.
    assert len(train[0]) + len(val[0]) + len(test[0]) == len(orig_dataset)

    # Check that the splits are disjoint.
    train_set = set(target.item() for target in train[1])
    val_set = set(target.item() for target in val[1])
    test_set = set(target.item() for target in test[1])
    assert not train_set.intersection(val_set)
    assert not train_set.intersection(test_set)
    assert not val_set.intersection(test_set)

    # Check that the scaling values are saved correctly.
    features, targets = next(
        iter(orig_dataset.batch(batch_size=len(orig_dataset)).as_numpy_iterator())
    )

    with (scalings_path / "scalings.csv").open() as csvfile:
        lines = csvfile.readlines()
        assert lines[0].strip() == "variable,min,max"
        for i, line in enumerate(lines[1 : len(feature_names) + 1]):
            name, min_value, max_value = line.strip().split(",")
            assert name == f"input_feat_{i}"
            assert pytest.approx(float(min_value), abs=1e-7) == np.min(features[..., i])
            assert pytest.approx(float(max_value), abs=1e-7) == np.max(features[..., i])
        name, min_value, max_value = lines[len(feature_names) + 1].strip().split(",")
        assert name == "output_WI"
        assert pytest.approx(float(min_value), abs=1e-7) == np.min(targets)
        assert pytest.approx(float(max_value), abs=1e-7) == np.max(targets)
        assert lines[len(feature_names) + 2].strip() == "feature_range,0,1"
        assert lines[len(feature_names) + 3].strip() == "target_range,0,1"

    # Load and transform the unshuffled target data.
    _, unshuffled_train_targets = next(
        iter(orig_train.batch(batch_size=len(orig_train)).as_numpy_iterator())
    )

    _, unshuffled_val_targets = next(
        iter(orig_val.batch(batch_size=len(orig_val)).as_numpy_iterator())
    )
    _, unshuffled_test_targets = next(
        iter(orig_test.batch(batch_size=len(orig_test)).as_numpy_iterator())
    )
    unshuffled_train_targets = target_scaler.transform(unshuffled_train_targets)
    unshuffled_val_targets = target_scaler.transform(unshuffled_val_targets)
    unshuffled_test_targets = target_scaler.transform(unshuffled_test_targets)

    # Check that the dataset is shuffled correctly.
    # There is a small chance this will fail for shuffle == "first" and shuffle ==
    # "last", when shuffling returns the original order by accident.
    if shuffle == "first":
        assert_raises(
            AssertionError, assert_allclose, train[1], unshuffled_train_targets
        )
        assert_raises(AssertionError, assert_allclose, val[1], unshuffled_val_targets)
        assert_raises(AssertionError, assert_allclose, test[1], unshuffled_test_targets)
        assert_raises(
            AssertionError,
            assert_allclose,
            np.sort(train[1], axis=0),
            unshuffled_train_targets,
        )

        assert_raises(
            AssertionError,
            assert_allclose,
            np.sort(val[1], axis=0),
            unshuffled_val_targets,
        )
        assert_raises(
            AssertionError,
            assert_allclose,
            np.sort(test[1], axis=0),
            unshuffled_test_targets,
        )
    elif shuffle == "last":
        assert_raises(
            AssertionError, assert_allclose, train[1], unshuffled_train_targets
        )
        assert_raises(AssertionError, assert_allclose, val[1], unshuffled_val_targets)
        assert_raises(AssertionError, assert_allclose, test[1], unshuffled_test_targets)
        assert_allclose(np.sort(train[1], axis=0), unshuffled_train_targets)
        assert_allclose(np.sort(val[1], axis=0), unshuffled_val_targets)
        assert_allclose(np.sort(test[1], axis=0), unshuffled_test_targets)
    elif shuffle == "false":
        assert_allclose(train[1], unshuffled_train_targets)
        assert_allclose(val[1], unshuffled_val_targets)
        assert_allclose(test[1], unshuffled_test_targets)
