# pylint: disable=fixme
"""Analyze the sensitivity of a neural network to its inputs.

Inspiration taken from
https://f0nzie.github.io/machine_learning_compilation/sensitivity-analysis-for-a-neural-network.html

"""

from __future__ import annotations

import math
import pathlib
from typing import Literal, Optional

import numpy as np
from matplotlib import pyplot as plt
from tensorflow import keras

from pyopmnearwell.utils import plotting


def sensitivity_analysis(
    model: keras.Model,
    resolution_1: int = 20,
    resolution_2: int = 20,
    mode: (
        Literal["homogeneous", "random_uniform", "random_normal"] | float
    ) = "homogeneous",
) -> tuple[np.ndarray, np.ndarray]:
    """Perform a sensitivity analysis of a neural network.

    For each input variable, vary from a min to a max value and measure how the output
    of the network changes. The other input variables are kept constant meanwhile.

    Note: It is assumed that the network has a single output.

    Args:
        model (keras.Model): Neural network.
        resolution_1 (int): Number of different values that the fixed inputs take.
            Equals the number of plotted lines in ``plot_analysis``.
        resolution_2 (int): Number of different values the variable input takes. Equals
            the number of datapoints along the x-axis ``plot_analysis``.
        mode (Literal["homogeneous", "random_uniform", "random_normal"] | float): Sets
            the sampling mode for the fixed inputs.
            - "homogeneous":
            - "random_uniform":
            - "random_normal"
            - float: All fixed inputs are set to this value.
            Default is "homogeneous".

    Returns:
        tuple[np.ndarray, np.ndarray]: Output and inputs from the sensitivity analysis.
        First axis is the input variable that is varying, second axis is the variation,
        third axis is the variation for the fixed variables. The input array contains an
        additional axis in case of input dimension > 1.

    """
    # Get the number of input variables.
    num_inputs = model.input_shape[1]

    # Get the minimum and maximum values for each input variable
    # min_values = np.min(model.input, axis=0)
    # max_values = np.max(model.input, axis=0)

    # We assume the model is normalized such that each input variable has min value -1
    # and max value 1.
    # TODO: Add options for when this is not the case.
    min_values: np.ndarray = np.full((num_inputs,), -1)
    max_values: np.ndarray = np.full((num_inputs,), 1)

    # Initialize the inputs and outputs array.
    inputs: np.ndarray = np.zeros((num_inputs, resolution_1, resolution_2, num_inputs))
    outputs: np.ndarray = np.zeros((num_inputs, resolution_1, resolution_2))

    # Initialize random generators.
    if isinstance(mode, str) and mode.startswith("random"):
        rng: np.random.Generator = np.random.default_rng()

    # Iterate over all input variables. For each variable and constant input vector, we
    # create a batch of input arrays and evaluate outside the innermost for loop,
    # instead of evaluating on single-point batches.
    for i in range(num_inputs):
        # Create input arrays for the fixed variables.
        if mode == "homogeneous":
            # fixed_inputs: np.ndarray = np.repeat(
            #     np.linspace(min_values, max_values, resolution_1)[..., None],
            #     num_inputs,
            #     axis=-1,
            # )
            fixed_inputs: np.ndarray = np.linspace(min_values, max_values, resolution_1)
        elif mode == "random_uniform":
            # Get uniform distribution on [0,1) and scale to (min_value, max_value).
            # pylint: disable-next=possibly-used-before-assignment
            fixed_inputs = rng.uniform(
                min_values, max_values, size=(resolution_1, num_inputs)
            )
        elif mode == "random_normal":
            # Set standard deviation s.t. ~95% of the inputs are inside the [min_values,
            # max_values] interval.
            fixed_inputs = rng.normal(
                max_values - min_values,
                (max_values - min_values) / 4,
                size=(resolution_1, num_inputs),
            )
        elif isinstance(mode, float):
            fixed_inputs = np.full((resolution_1, num_inputs), mode)
        else:
            raise ValueError("'mode' has invalid value")
        for j, fixed_input in enumerate(fixed_inputs):
            assert fixed_input.shape == (num_inputs,)
            fixed_input = np.tile(fixed_input, (resolution_2, 1))

            # Replace i-th input with varying value.
            fixed_input[..., i] = np.linspace(
                min_values[i], max_values[i], resolution_2
            )

            predictions = model.predict(fixed_input)

            assert fixed_input.shape == (resolution_2, num_inputs)
            assert predictions.shape == (resolution_2, 1)

            outputs[i, j] = predictions.flatten()
            inputs[i, j] = fixed_input

    return outputs, inputs


def plot_analysis(
    outputs: np.ndarray,
    inputs: np.ndarray,
    savepath: str | pathlib.Path,
    feature_names: Optional[list[str]] = None,
    main_plot: Optional[tuple[np.ndarray, np.ndarray]] = None,
    **kwargs,
) -> None:
    r"""
    Plot the analysis of the model outputs against inputs.

    Args:
        outputs (np.ndarray): The model outputs.
        inputs (np.ndarray): The model inputs. Shape is ``(num_inputs, resolution_1,
        resolution_2)``.
        savepath (str | pathlib.Path): The path to save the plot.
        feature_names (Optional[list[str]]): The names of the input features. If None,
        default names (:math:`x_1,x_2,\dots`) will be used. Default is None.
        main_plot (Optional[tuple[np.ndarray, np.ndarray]]): Add output and input for a
            main plot that is specifically highlighted. Default is None.
        **kwargs:
            - legend (bool): Whether to plot a legend. Default
              is True.

    Returns:
        None

    """
    if feature_names is None:
        feature_names = [rf"$x_{{{i}}}$" for i in range(inputs.shape[-1])]
    elif len(feature_names) != inputs.shape[-1]:
        raise ValueError

    # Max ``max_columns`` (default=3) columns and increase figure size.
    num_rows: int = math.ceil(outputs.shape[0] / kwargs.get("max_columns", 3))
    num_columns: int = min(outputs.shape[0], kwargs.get("max_columns", 3))

    fig, axes = plt.subplots(
        num_rows,
        num_columns,
        sharex=True,
        sharey=True,
        # NOTE: Setting the figure size here does not work.
        # figheight=max(num_rows * 3, 5),
        # figwidth=max(num_columns * 3, 5)
        # size_inches=(max(num_columns * 3, 5), max(num_rows * 3, 5)),
    )
    fig.set_size_inches(w=max(num_columns * 3, 5), h=max(num_rows * 3, 5))

    # mypy complains that ``axes`` might not have an attribute ``.flatten()``, but this
    # shouldn't be a problem.
    for i, ax in enumerate(
        axes.flatten()  # type: ignore # pylint: disable=invalid-name
    ):
        # If not all rows are full, there are more axes than features. Skip the last few
        # axes.
        if i >= len(feature_names):
            break
        for j, color in enumerate(
            # Ignore mypy complaining about ``cm`` not being a module.
            # pylint: disable-next=no-member
            plt.cm.Blues(np.linspace(0.3, 0.7, outputs.shape[1])),  # type: ignore
        ):
            ax.plot(
                inputs[i, j, :, i],
                outputs[i, j],
                color=color,
                linestyle=":",
                label=f"{inputs[i, j, 0, i - 1]}",
            )
        if main_plot is not None:
            ax.plot(
                main_plot[1][i, 0, :, i],
                main_plot[0][i, 0],
                color="blue",
                label="0",
            )
        ax.set_title(feature_names[i])

    # Create common axes for all subplots. Add a big axis, hide frame.
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

    if kwargs.get("legend", True):
        # pylint: disable-next=undefined-loop-variable
        ax.legend(title="Splits", loc="center left", bbox_to_anchor=(1, 0.5))

    plotting.save_fig_and_data(fig, savepath)
