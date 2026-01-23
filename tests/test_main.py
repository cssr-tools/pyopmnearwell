# SPDX-FileCopyrightText: 2023-2025, NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=missing-function-docstring
"""Test the main framework."""

import pathlib


def test_main(run_main: pathlib.Path) -> None:
    assert (run_main / "output" / "output" / "INPUT.UNRST").exists()
