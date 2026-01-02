# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Case 2 in the publication. To generate Figure 7, this can be achieved using plopm by executing:
plopm -i well_adaptive_injection/output/WELL_ADAPTIVE_INJECTION -v saltp -z 0 -x '[0,20]' -c coolwarm
plopm -i 'well_adaptive_injection/output/WELL_ADAPTIVE_INJECTION well_uniform_injection/output/WELL_UNIFORM_INJECTION' -v 'saltp * rporv * 2153' -s 1,1,: -how mean
plopm -i . -v fpr -tunits y -xformat .1f -xlnum 6 -yformat .1f -ylnum 7
plopm -i . -v fgmds -tunits y -xformat .1f -xlnum 6 -ylabel 'Mass [kg]' -t 'Total dissolved CO$_2$' -yformat .1E
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
    command += f"pyopmnearwell -i {name}.toml -o {name} & "
command += "wait"
os.system(command)
