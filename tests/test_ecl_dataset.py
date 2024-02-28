# pylint: disable=missing-function-docstring, invalid-name
"""Test the data module.

We disable quite a lot of pylint errors, as it struggles with the pytest fictures and so
on.

"""


import pathlib

import numpy as np
import pytest
import tensorflow as tf
from ecl.eclfile.ecl_file import EclFile, open_ecl_file

from pyopmnearwell.ml.ecl_dataset import EclDataSet

dirname: pathlib.Path = pathlib.Path(__file__).parent


@pytest.fixture(name="EclKW_saturation")
def fixture_EclKW_saturation() -> np.ndarray:
    with open_ecl_file(str(dirname / "data" / "DUMMY.UNRST")) as ecl_file:
        saturation_array = np.array(ecl_file.iget_kw("SGAS"))
        # Transform to model input shape (no batch).
        return np.expand_dims(saturation_array, axis=-1)


@pytest.fixture(name="EclKW_pressure")
def fixture_EclKW_pressure() -> np.ndarray:
    with open_ecl_file(str(dirname / "data" / "DUMMY.UNRST")) as ecl_file:
        pressure_array = np.array(ecl_file.iget_kw("PRESSURE"))
        # Transform to model output shape (no batch).
        return np.expand_dims(pressure_array, axis=-1)


@pytest.fixture(name="Ecl_dummy_file")
def fixture_Ecl_dummy_file() -> EclFile:
    """Return a dummy ``EclFile``."""
    ecl_file = EclFile(str(dirname / "data" / "DUMMY.UNRST"))
    return ecl_file


@pytest.fixture(name="Ecl_data_set")
def fixture_Ecl_data_set() -> EclDataSet:
    dataset = EclDataSet(
        path=str(dirname),
        input_kws=["PRESSURE"],
        target_kws=["SGAS"],
        read_data_on_init=False,
    )
    return dataset


# def test_ECLDataSet(Ecl_dummy_file: EclFile, Ecl_data_set: EclDataSet) -> None:
#     """_summary_

#     Parameters:
#         ECL_dummy_file: _description_
#     """
#     pass


def test_EclFile_to_datapoint(
    Ecl_data_set: EclDataSet,
    Ecl_dummy_file: EclFile,
    EclKW_pressure: np.ndarray,
    EclKW_saturation: np.ndarray,
) -> None:
    """Test the ``EclFile_to_datapoint`` method.

    Parameters:
        ECL_dummmy_file: _description_
        Ecl_data_set: _description_
    """
    feature, target = Ecl_data_set.EclFile_to_datapoint(Ecl_dummy_file)
    assert np.allclose(feature, EclKW_pressure)
    assert np.allclose(target, EclKW_saturation)


def test_ECLDataSet_read_data(Ecl_data_set: EclDataSet) -> None:
    """Test that ``EclDataSet.read_data`` runs without any error.

    Parameters:
        Ecl_data_set: _description_

    """
    Ecl_data_set.read_data()


def test_ECLDataSet_on_epoch_end(Ecl_data_set: EclDataSet) -> None:
    """Test that ``EclDataSet.on_epoch_end`` runs without any error.

    Parameters:
        Ecl_data_set: _description_

    """
    Ecl_data_set.read_data()
    Ecl_data_set.on_epoch_end()


def test_ECLDataSet_len(Ecl_data_set: EclDataSet) -> None:
    """Test that ``EclDataSet.__len__`` is greater than zero."""
    Ecl_data_set.read_data()
    assert len(Ecl_data_set) > 0


def test_tfDataset_from_ECLDataSet_len(Ecl_data_set: EclDataSet) -> None:
    """Test that a ``tf.data.Dataset`` generated from ``EclDataSet`` has length greater
    than zero."""
    Ecl_data_set.read_data()
    ds = tf.data.Dataset.from_generator(
        Ecl_data_set,
        output_signature=(
            tf.TensorSpec.from_tensor(Ecl_data_set[0][0]),  # type: ignore
            tf.TensorSpec.from_tensor(Ecl_data_set[0][1]),  # type: ignore
        ),
    )

    ds = ds.apply(tf.data.experimental.assert_cardinality(len(Ecl_data_set)))
    assert tf.data.experimental.cardinality(ds).numpy() == len(Ecl_data_set)
