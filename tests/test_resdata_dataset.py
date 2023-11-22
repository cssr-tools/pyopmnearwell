# pylint: disable=missing-function-docstring, invalid-name
"""Test the ``resdata_dataset`` module."""


import pathlib

import numpy as np
import pytest
import tensorflow as tf
from resdata import FileMode
from resdata.resfile import ResdataFile

from pyopmnearwell.ml.resdata_dataset import ResDataSet

dirname: pathlib.Path = pathlib.Path(__file__).parent


@pytest.fixture(name="ResdataKW_saturation")
def fixture_ResdataKW_saturation() -> np.ndarray:
    file = ResdataFile(
        str(dirname / "data" / "DUMMY.UNRST"), flags=FileMode.CLOSE_STREAM
    )
    saturation_array = np.array(file.iget_kw("SGAS"))
    # Transform to model input shape (no batch).
    return np.expand_dims(saturation_array, axis=-1)


@pytest.fixture(name="ResdataKW_pressure")
def fixture_ResdataKW_pressure() -> np.ndarray:
    file = ResdataFile(
        str(dirname / "data" / "DUMMY.UNRST"), flags=FileMode.CLOSE_STREAM
    )
    pressure_array = np.array(file.iget_kw("PRESSURE"))
    # Transform to model output shape (no batch).
    return np.expand_dims(pressure_array, axis=-1)


@pytest.fixture(name="dummy_ResdataFile")
def fixture_dummy_ResdataFile() -> ResdataFile:
    """Return a dummy ``EclFile``."""
    file = ResdataFile(
        str(dirname / "data" / "DUMMY.UNRST"), flags=FileMode.CLOSE_STREAM
    )
    return file


@pytest.fixture(name="dataset")
def fixture_dataset() -> ResDataSet:
    dataset = ResDataSet(
        path=str(dirname),
        input_kws=["PRESSURE"],
        target_kws=["SGAS"],
        read_data_on_init=False,
    )
    return dataset


def test_EclFile_to_datapoint(
    dataset: ResDataSet,
    dummy_ResdataFile: ResdataFile,
    ResdataKW_pressure: np.ndarray,
    ResdataKW_saturation: np.ndarray,
) -> None:
    """Test the ``EclFile_to_datapoint`` method.

    This function tests the functionality of the ``EclFile_to_datapoint`` method in the
    ``ResDataSet`` class. It verifies whether the method correctly converts an EclFile
    object into a feature and target datapoint.


    Args:
        Ecl_data_set (ResDataSet): An instance of the ResDataSet class.
        Ecl_dummy_file (EclFile): An EclFile object to be converted.
        Resdata
    KW_pressure (np.ndarray): The expected pressure values of the converted
            datapoint.
        ResdataKW_saturation (np.ndarray): The expected saturation values of the converted
            datapoint.

    Returns:
        None

    """
    feature, target = dataset.ResdataFile_to_datapoint(dummy_ResdataFile)
    assert np.allclose(feature, ResdataKW_pressure)
    assert np.allclose(target, ResdataKW_saturation)


def test_ResDataSet_read_data(dataset: ResDataSet) -> None:
    """Test that ``ResDataSet.read_data`` runs without any error.

    Args:
        Ecl_data_set (ResDataSet): _description_

    """
    dataset.read_data()


def test_ResDataSet_on_epoch_end(dataset: ResDataSet) -> None:
    """Test that ``ResDataSet.on_epoch_end`` runs without any error.

    Args:
        Ecl_data_set (ResDataSet): _description_

    """
    dataset.read_data()
    dataset.on_epoch_end()


def test_ResDataSet_len(dataset: ResDataSet) -> None:
    """Test that ``ResDataSet.__len__`` is greater than zero."""
    dataset.read_data()
    assert len(dataset) > 0


def test_tfDataset_from_ResDataSet_len(dataset: ResDataSet) -> None:
    """Test that a ``tf.data.Dataset`` generated from ``ResDataSet`` has length greater
    than zero."""
    dataset.read_data()
    ds = tf.data.Dataset.from_generator(
        dataset,
        output_signature=(
            tf.TensorSpec.from_tensor(dataset[0][0]),  # type: ignore
            tf.TensorSpec.from_tensor(dataset[0][1]),  # type: ignore
        ),
    )

    ds = ds.apply(tf.data.experimental.assert_cardinality(len(dataset)))
    assert tf.data.experimental.cardinality(ds).numpy() == len(dataset)
