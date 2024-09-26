# pylint: disable=missing-function-docstring, fixme
"""Tests for the ``pyopmnearwell.ml.analysis`` module.


TODO: Set ``mock_model`` to a linear model and check that the relations betweens outputs
and inputs of ``sensitivity_analysis`` are also linear.

"""

import keras
import numpy as np
import pytest

from pyopmnearwell.ml.analysis import plot_analysis, sensitivity_analysis


@pytest.fixture(name="mock_model")
def fixture_mock_model() -> keras.Model:
    # Create a mock model for testing
    model = keras.Sequential()
    model.add(keras.layers.Dense(1, input_shape=(2,)))
    model.compile(optimizer="adam", loss="mse")
    return model


@pytest.fixture(params=[1, 10], name="resolution_1")
def fixture_resolution_1(request) -> int:
    return request.param


@pytest.fixture(params=[1, 10], name="resolution_2")
def fixture_resolution_2(request) -> int:
    return request.param


@pytest.fixture(name="run_sensitivity_analysis")
def fixture_run_sensitivity_analysis(
    mock_model: keras.Model, resolution_1: int, resolution_2: int
) -> tuple[np.ndarray, np.ndarray]:
    return sensitivity_analysis(mock_model, resolution_1, resolution_2)


def test_sensitivity_analysis(
    run_sensitivity_analysis: tuple[np.ndarray, np.ndarray],
    resolution_1: int,
    resolution_2: int,
) -> None:
    """Test the sensitivity_analysis function.

    Args:
        run_sensitivity_analysis (tuple[np.ndarray, np.ndarray]): Output from
            ``run_sensitivity_analysis``.
        resolution_1 (int): The resolution for the first dimension.
        resolution_2 (int): The resolution for the second dimension.

    Returns:
        None

    """
    outputs, inputs = run_sensitivity_analysis

    expected_output_shape: tuple = (2, resolution_1, resolution_2)
    expected_input_shape: tuple = expected_output_shape + (2,)

    # Check shapes.
    assert outputs.shape == expected_output_shape
    assert inputs.shape == expected_input_shape

    # Check that the outputs are not all zeros.
    assert not np.allclose(outputs, 0)

    # Check ranges.
    assert np.all(inputs >= -1)
    assert np.all(inputs <= 1)


def test_plot_analysis(
    run_sensitivity_analysis: tuple[np.ndarray, np.ndarray],
    tmp_path,
) -> None:
    """Test the plot_analysis function.

    Args:
        sensitivity_analysis_results (tuple[np.ndarray, np.ndarray]): Output from
            ``run_sensitivity_analysis``.
        tmp_path (pathlib.Path):

    Returns:
        None

    """
    outputs, inputs = run_sensitivity_analysis
    plot_analysis(outputs, inputs, tmp_path / "save")

    assert (tmp_path / "save.pickle").is_file()
    assert (tmp_path / "save.svg").is_file()
