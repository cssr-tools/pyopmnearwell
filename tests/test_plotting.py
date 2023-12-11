# pylint: skip-file
from __future__ import annotations

import pathlib
import pickle

import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

from pyopmnearwell.utils.plotting import save_fig_and_data


def test_save_fig_and_data(tmp_path: pathlib.Path):
    # Create a pyplot figure
    fig, ax = plt.subplots()
    plt.plot([1, 2, 3], [4, 5, 6])

    # Save the figure and data
    save_fig_and_data(fig, tmp_path / "test")

    # Check that the figure was saved correctly
    assert (tmp_path / "test.svg").is_file()
    assert (tmp_path / "test.pickle").is_file()

    # Check that the data was saved correctly
    # # TODO: Fix this.
    # with open(pathlib.Path(tmp_path) / "test.pickle", "rb") as f:
    #     loaded_fig: Figure = pickle.load(f)
    #     assert fig == loaded_fig
