# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1732

"""Case 3 in the publication"""

import subprocess
from pathlib import Path

whr = Path(__file__).resolve().parent

NAMES = [
    "higher_top_to_lower_bottom_capillary_number",
    "lower_top_to_higher_bottom_capillary_number",
    "homogeneous_equivalent_system",
]
LABELS = "higher top to lower  lower top to lower  homogeneous"
command_processes = []
for i, name in enumerate(NAMES):
    command_processes.append(
        subprocess.Popen(
            [
                "pyopmnearwell",
                "-i",
                f"{whr}/{name}.toml",
                "-o",
                f"{whr}/{name}",
                "-m",
                "single",
            ]
        )
    )
for process in command_processes:
    process.wait()

CASE = "higher_top_to_lower_bottom_capillary_number/HIGHER_TOP_TO_LOWER_BOTTOM_CAPILLARY_NUMBER"
command_processes = []
command_processes.append(
    subprocess.Popen(
        [
            "plopm",
            "-i",
            CASE,
            "-v",
            "permx",
            "-z",
            "0",
            "-c",
            "Pastel1",
            "-cnum",
            "4",
        ]
    )
)
command_processes.append(
    subprocess.Popen(["plopm", "-i", CASE, "-v", "sgas", "-z", "0", "-x", "[0,20]"])
)
command_processes.append(
    subprocess.Popen(
        [
            "plopm",
            "-i",
            CASE,
            "-v",
            "saltp",
            "-z",
            "0",
            "-x",
            "[0,20]",
            "-c",
            "coolwarm",
        ]
    )
)
command_processes.append(
    subprocess.Popen(["plopm", "-i", ".", "-v", "wbhp:inj0", "-labels", LABELS])
)
for process in command_processes:
    process.wait()
