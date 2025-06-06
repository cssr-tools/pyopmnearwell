# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Case 3 in the publication. To generate Figure 8 and 9, this can be achieved using plopm by executing:
plopm -i higher_top_to_lower_bottom_capillary_number/output/HIGHER_TOP_TO_LOWER_BOTTOM_CAPILLARY_NUMBER -v permx -z 0 -c Pastel1 -cnum 4
plopm -i higher_top_to_lower_bottom_capillary_number/output/HIGHER_TOP_TO_LOWER_BOTTOM_CAPILLARY_NUMBER -v sgas -z 0 -x '[0,20]'
plopm -i higher_top_to_lower_bottom_capillary_number/output/HIGHER_TOP_TO_LOWER_BOTTOM_CAPILLARY_NUMBER -v saltp -z 0 -x '[0,20]' -c coolwarm
plopm -i . -v wbhp:inj0
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
    command += f"pyopmnearwell -i {name}.toml -o {name} & "
command += "wait"
os.system(command)
