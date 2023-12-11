"""_summary_

Inspiration taken from
https://f0nzie.github.io/machine_learning_compilation/sensitivity-analysis-for-a-neural-network.html

"""

from __future__ import annotations

import pathlib

import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from tensorflow import keras

from pyopmnearwell.utils import plotting


def sensitivity_analysis(
    model: keras.Model, resolution_1: int = 20, resolution_2: int = 20
) -> tuple[np.ndarray, np.ndarray]:
    """Perform a sensitivity analysis of a neural network.

    For each input variable, vary from a min to a max value and measure how the output
    of the network changes. The other input variables are kept constant meanwhile.

    Note: It is assumed that the network has a single output.

    Args:
        model (keras.Model): Neural network.
        resolution_1 (int):
        resolution_2 (int):

    Returns:
        np.ndarray: Output from the sensitivity analysis. First axis is the input
        variable that is varying, second axis is the variation.

    """
    # Get the number of input variables.
    num_inputs = model.input_shape[1]

    # Get the minimum and maximum values for each input variable
    # min_values = np.min(model.input, axis=0)
    # max_values = np.max(model.input, axis=0)

    # We assume the model is normalized such that each input variable has min value 0
    # and max value 1.
    # TODO: Add options when this is not the case.
    min_values: np.ndarray = np.full((num_inputs,), -1)
    max_values: np.ndarray = np.full((num_inputs,), 1)

    # Initialize the inputs and outputs array
    inputs: np.ndarray = np.zeros((num_inputs, resolution_1, resolution_2, num_inputs))
    outputs: np.ndarray = np.zeros((num_inputs, resolution_1, resolution_2))

    # Iterate over all input variables. For each variable and constant input vector, we
    # create a batch of input arrays and evaluate outside the innermost for loop.
    for i in range(num_inputs):
        # Create constant input arrays for all other variables.
        constant_inputs: np.ndarray = np.linspace(min_values, max_values, resolution_1)

        for j, constant_input in enumerate(constant_inputs):
            assert constant_input.shape == (num_inputs,)
            input: np.ndarray = np.tile(constant_input, (resolution_2, 1))

            # Replace i-th input with varying value.
            input[..., i] = np.linspace(min_values[i], max_values[i], resolution_2)

            predictions = model.predict(input)

            assert input.shape == (resolution_2, num_inputs)
            assert predictions.shape == (resolution_2, 1)

            outputs[i, j] = predictions.flatten()
            inputs[i, j] = input

    return outputs, inputs


def plot_analysis(
    outputs: np.ndarray, inputs: np.ndarray, savepath: str | pathlib.Path
) -> None:
    """_summary_

    Args:
        outputs (np.ndarray): _description_
        inputs (np.ndarray): _description_. Shape is ``(num_inputs, resolution_1,
            resolution_2)``.
        savepath (str | pathlib.Path):

    Returns:
        None

    """
    fig, axes = plt.subplots(
        1,
        outputs.shape[0],
        sharex=True,
        sharey=True,
    )
    for i, ax in enumerate(axes):
        # Ignore mypy complaining about ``cm`` not being a module.
        for j, color in enumerate(plt.cm.Blues(np.linspace(0.3, 1, outputs.shape[1]))):  # type: ignore
            ax.plot(
                inputs[i, j, :, i],
                outputs[i, j],
                color=color,
                label=f"{inputs[i, j, 0, i - 1]}",
            )
            ax.set_title(rf"$x_{i}$")

    # Add a big axis, hide frame.
    fig.add_subplot(111, frameon=False)
    # Set common x and y labels.
    plt.tick_params(
        labelcolor="none",
        which="both",
        top=False,
        bottom=False,
        left=False,
        right=False,
    )
    plt.xlabel("Explanatory")
    plt.ylabel("Response")
    plt.legend(title="Splits", loc="center left", bbox_to_anchor=(1, 0.5))
    plotting.save_fig_and_data(fig, savepath)
