# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os

NAMES = ["higher_to_lower", "lower_to_higher", "homogeneous"]
os.system("rm -rf compare")
command = ""
for i, name in enumerate(NAMES):
    os.system(f"rm -rf {name}")
    command += f"pyopmnearwell -i {name}.txt -o {name} -p opm & "
command += "wait"
os.system(command)
os.system("pyopmnearwell -c compare -p opm -m saltprec")
