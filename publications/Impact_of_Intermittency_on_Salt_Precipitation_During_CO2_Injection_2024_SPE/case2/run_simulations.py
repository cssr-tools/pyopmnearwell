# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os

NAMES = [
    "base_system",
    "no_adaptive_injection",
    "no_cp-jfunc_correction",
    "no_hysteresis",
    "no_log_extension",
    "no_salt_precipitation",
]
os.system("rm -rf compare")
nsimulations = len(NAMES)
command = ""
for i, name in enumerate(NAMES):
    os.system(f"rm -rf {name}")
    command += f"pyopmnearwell -i {name}.txt -o {name} -p opm & "
command += "wait"
os.system(command)
os.system("pyopmnearwell -c compare -p opm")
