# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

"""Test the main framework"""

import os
from pyopmnearwell.core.pyopmnearwell import main


def test():
    """See models/input.txt"""
    cwd = os.getcwd()
    os.chdir(f"{os.getcwd()}/tests/models")
    main()
    os.chdir(cwd)
