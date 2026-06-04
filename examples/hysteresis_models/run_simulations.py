# SPDX-FileCopyrightText: 2025 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1732

"""Script to run pyopmnearwell with different hysteresis models. It requires plopm:
https://github.com/cssr-tools/plopm"""

import subprocess
from mako.template import Template

command_processes = []
for name in ["nohysteresis", "Carlson", "Killough"]:
    mytemplate = Template(filename="co2.mako")
    var = {"name": name}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"co2_{name}.toml",
        "w",
        encoding="utf8",
    ) as f:
        f.write(filledtemplate)
    command_processes.append(
        subprocess.Popen(
            ["pyopmnearwell", "-i", f"co2_{name}.toml", "-o", f"{name}", "-m", "single"]
        )
    )
for process in command_processes:
    process.wait()

command_processes = []
for quan in ["tcpu", "msumlins", "msumnewt", "fgip", "wbhp:inj0", "fgir"]:
    command_processes.append(
        subprocess.Popen(
            [
                "plopm",
                "-i",
                "nohysteresis/CO2_NOHYSTERESIS Carlson/CO2_CARLSON Killough/CO2_KILLOUGH",
                "-v",
                f"{quan}",
            ]
        )
    )
for process in command_processes:
    process.wait()
