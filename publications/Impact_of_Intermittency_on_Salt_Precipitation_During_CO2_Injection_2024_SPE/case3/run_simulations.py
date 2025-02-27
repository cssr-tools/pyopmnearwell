# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os

NAMES = [
    "higher_top_to_lower_bottom_capillary_number",
    "lower_top_to_higher_bottom_capillary_number",
    "homogeneous_equivalent_system",
]
os.system("rm -rf compare")
command = ""
for i, name in enumerate(NAMES):
    os.system(f"rm -rf {name}")
    command += f"pyopmnearwell -i {name}.toml -o {name} -p opm & "
command += "wait"
os.system(command)
os.system("pyopmnearwell -c compare -p opm -m saltprec")
