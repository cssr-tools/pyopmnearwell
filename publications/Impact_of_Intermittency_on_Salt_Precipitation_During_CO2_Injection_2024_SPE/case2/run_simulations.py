# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os

NAMES = [
    "well_adaptive_injection",
    "well_adaptive_injection_no_salt_precipitation",
    "well_uniform_injection",
    "well_uniform_injection_no_salt_precipitation",
]
os.system("rm -rf compare")
nsimulations = len(NAMES)
command = ""
for i, name in enumerate(NAMES):
    os.system(f"rm -rf {name}")
    command += f"pyopmnearwell -i {name}.toml -o {name} -p opm & "
command += "wait"
os.system(command)
os.system("pyopmnearwell -c compare -p opm")
