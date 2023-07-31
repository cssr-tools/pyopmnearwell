import os

import numpy as np
import pytest
import tensorflow as tf
from ecl import EclFileFlagEnum
from ecl.ecl_type import EclDataType
from ecl.eclfile.ecl_file import EclFile, EclKW, open_ecl_file

from pyopmnearwell.ml.data import EclDataSet

dir_path = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def EclKW_saturation() -> np.ndarray:
    with open_ecl_file(os.path.join(dir_path, "DUMMY.UNRST")) as ecl_file:
        saturation_array = np.array(ecl_file.iget_kw("SGAS"))
        # Transform to model input shape (no batch).
        return np.expand_dims(saturation_array, axis=-1)


@pytest.fixture
def EclKW_pressure() -> np.ndarray:
    with open_ecl_file(os.path.join(dir_path, "DUMMY.UNRST")) as ecl_file:
        pressure_array = np.array(ecl_file.iget_kw("PRESSURE"))
        # Transform to model output shape (no batch).
        return np.expand_dims(pressure_array, axis=-1)


@pytest.fixture
def Ecl_dummy_file(EclKW_saturation: EclKW, EclKW_pressure: EclKW) -> EclFile:
    """Return a dummy ``EclFile``."""
    ecl_file = EclFile(os.path.join(dir_path, "DUMMY.UNRST"))
    return ecl_file


@pytest.fixture
def Ecl_data_set() -> EclDataSet:
    ds = EclDataSet(
        path=dir_path,
        input_kws=["PRESSURE"],
        target_kws=["SGAS"],
        read_data_on_init=False,
    )
    return ds


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
    input, target = Ecl_data_set.EclFile_to_datapoint(Ecl_dummy_file)
    assert np.allclose(input, EclKW_pressure)
    assert np.allclose(target, EclKW_saturation)


def test_ECLDataSet_read_data(
    Ecl_data_set: EclDataSet,
) -> None:
    """Test that ``EclDataSet.read_data`` runs without any error.

    Parameters:
        Ecl_data_set: _description_

    """
    Ecl_data_set.read_data()


def test_ECLDataSet_on_epoch_end(
    Ecl_data_set: EclDataSet,
) -> None:
    """Test that ``EclDataSet.on_epoch_end`` runs without any error.

    Parameters:
        Ecl_data_set: _description_

    """
    Ecl_data_set.read_data()
    Ecl_data_set.on_epoch_end()
