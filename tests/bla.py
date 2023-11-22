# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the different type of grids"""

import os
import pathlib
import shutil

import pytest

dirname: pathlib.Path = pathlib.Path(__file__).parent


@pytest.fixture
def prepare_tmp_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    """Copy pyopmnearwell decks to tmp_path.

    Args:
        tmp_path (_type_): Temporary dir. Provided by pytest.

    Returns:
        pathlib.Path: Temporary dir containing all pyopmnearwell decks from
            tests/geometries.

    """
    conf_fil = sorted([name.name for name in (dirname / "geometries").iterdir()])
    for file in conf_fil:
        shutil.copyfile(dirname / "geometries" / file, tmp_path / file)
    return tmp_path


def test_geometries(prepare_tmp_dir: pathlib.Path):
    """See geometries/"""
    # cwd = os.getcwd()
    # os.chdir(f"{os.getcwd()}/tests/geometries")
    # conf_fil = sorted([name[:-4] for name in os.listdir(".") if
    # name.endswith(".txt")])
    os.chdir(prepare_tmp_dir)
    conf_fil = sorted([name.stem for name in prepare_tmp_dir.iterdir()])
    for file in conf_fil:
        command = f"pyopmnearwell -i {file}.txt -o {prepare_tmp_dir / file} & wait"
        print(command)
        os.system(command)
        assert (
            prepare_tmp_dir / file / "postprocessing" / "saturation_2D.png"
        ).exists()
    #     os.system(f"rm -rf {file}")
    # os.chdir(cwd)
