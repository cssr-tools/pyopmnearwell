# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the h2store model with the 3d cartesian grid."""

import os
import pathlib
import shutil

dirname: pathlib.Path = pathlib.Path(__file__).parent


def test_h2store(tmp_path):
    """See models/h2store.txt"""
    shutil.copy(dirname / "models" / "h2store.txt", tmp_path)
    os.chdir(tmp_path)
    os.system("pyopmnearwell -i h2store.txt -o h2store")
    assert (tmp_path / "h2store" / "postprocessing" / "pressure_2D.png").exists()
