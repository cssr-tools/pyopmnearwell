# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1732

"""Case 1 in the publication"""

import subprocess
from pathlib import Path
from mako.template import Template

whr = Path(__file__).resolve().parent

QRATE = [3, 5, 10, 15, 20, 30]
CASES = ["a", "b", "c", "d", "e", "f"]

HEIGHT = 100
PHI = 0.1
PERM = 101.3 / 1.01324997e15
RHOG = 636
MU = 4.8e-5
PE = 1.96e3
LC = 1
RD = 0.15

mytemplate = Template(filename=f"{whr}/salt.mako")
command_processes = []
for i, (case, qrate) in enumerate(zip(CASES, QRATE)):
    n_ca = (MU * qrate * LC) / (RHOG * PHI * PERM * PE * HEIGHT * 2 * 3.1416 * RD)
    var = {"qrate": qrate}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{whr}/{case}_nca_{n_ca:.0f}_M_{qrate}kg_s.toml",
        "w",
        encoding="utf8",
    ) as f:
        f.write(filledtemplate)
    command_processes.append(
        subprocess.Popen(
            [
                "pyopmnearwell",
                "-i",
                f"{whr}/{case}_nca_{n_ca:.0f}_M_{qrate}kg_s.toml",
                "-o",
                f"{whr}/{case}_nca_{n_ca:.0f}_M_{qrate}kg_s",
                "-m",
                "single",
            ]
        )
    )
for process in command_processes:
    process.wait()

command_processes = []
command_processes.append(
    subprocess.Popen(
        [
            "plopm",
            "-i",
            "a_nca_123_M_3kg_s/A_NCA_123_M_3KG_S",
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
            "a_nca_123_M_3kg_s/A_NCA_123_M_3KG_S",
            "-v",
            "sgas",
            "-z",
            "0",
            "-x",
            "[0,20]",
        ]
    )
)
command_processes.append(
    subprocess.Popen(
        [
            "plopm",
            "-i",
            "a_nca_123_M_3kg_s/A_NCA_123_M_3KG_S",
            "-v",
            "pressure",
            "-z",
            "0",
            "-x",
            "[0,20]",
            "-c",
            "seismic",
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
            "saltp",
            "-x",
            "[0,20]",
            "-s",
            ":,1,20",
            "-lw",
            "3,3,3,3,3,3",
        ]
    )
)
for process in command_processes:
    process.wait()
