"""Helper functions for plotting."""

from __future__ import annotations

import pathlib
import pickle

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def set_latex_params() -> None:
    """Set the LaTeX parameters for matplotlib.

    This function sets the font to be sans-serif and the text to be normal weight.

    Returns:
        None

    """
    font = {"family": "normal", "weight": "normal", "size": 16}
    matplotlib.rc("font", **font)
    plt.rcParams.update(
        {
            "text.usetex": True,
            "font.family": "sans-serif",
            "svg.fonttype": "path",
            "legend.columnspacing": 0.9,
            "legend.handlelength": 1.5,
            "legend.fontsize": 14,
            "lines.linewidth": 4,
            "axes.titlesize": 16,
            "axes.grid": True,
        }
    )


set_latex_params()


def save_fig_and_data(fig: Figure, path: str | pathlib.Path) -> None:
    """Save a pyplot figure to an ``.svg`` file and save the data to a ``.pickle`` file.

    Args:
        fig (matplotlib.figure.Figure): The figure to save.
        path (str | pathlib.Path): The path to save the figure and data to.

    Returns:
        None

    """
    # Convert to a path in case a string was passed.
    path = pathlib.Path(path)

    # Save the figure to a png file
    # NOTE: Convert filename to str to ensure this works. With fig, ax = plt.subplots()
    # the conversion is not necessary, but with fig = plt.figure() it is.
    fig.savefig(
        str(path.with_suffix(".svg")), bbox_inches="tight", format="svg", dpi=300
    )

    # Save the data to a pickle file
    with path.with_suffix(".pickle").open("wb") as f:  # pylint: disable=C0103
        pickle.dump(fig, f)

    plt.close(fig)
