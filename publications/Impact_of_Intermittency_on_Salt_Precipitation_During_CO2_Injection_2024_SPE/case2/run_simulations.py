# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1732,C0301

"""Case 2 in the publication"""

import subprocess
from pathlib import Path

whr = Path(__file__).resolve().parent

NAMES = [
    "well_adaptive_injection",
    "well_adaptive_injection_no_salt_precipitation",
    "well_uniform_injection",
    "well_uniform_injection_no_salt_precipitation",
]
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

LABELS = "Adapt inj  Adapt inj no saltprec  Uniform inj  Uniform inj no saltprec"
command_processes = []
command_processes.append(
    subprocess.Popen(
        [
            "plopm",
            "-i",
            "well_adaptive_injection/WELL_ADAPTIVE_INJECTION",
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
    subprocess.Popen(
        [
            "plopm",
            "-i",
            "well_adaptive_injection/WELL_ADAPTIVE_INJECTION well_uniform_injection/WELL_UNIFORM_INJECTION",
            "-v",
            "saltp * rporv * 2153",
            "-s",
            "1,1,:",
            "-how",
            "mean",
        ]
    )
)
command_processes.append(
    subprocess.Popen(
        [
            "plopm",
            "-i",
            ".",
            "-v",
            "fpr",
            "-xformat",
            ".1f",
            "-xlnum",
            "6",
            "-yformat",
            ".1f",
            "-ylnum",
            "7",
            "-labels",
            LABELS,
        ]
    )
)
command_processes.append(
    subprocess.Popen(
        [
            "plopm",
            "-i",
            ".",
            "-v",
            "fgmds",
            "-xformat",
            ".1f",
            "-xlnum",
            "6",
            "-ylabel",
            "Mass [kg]",
            "-t",
            "Total dissolved CO$_2$",
            "-yformat",
            ".1E",
            "-labels",
            LABELS,
        ]
    )
)
for process in command_processes:
    process.wait()
