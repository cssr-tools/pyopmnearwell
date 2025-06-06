# SPDX-FileCopyrightText: 2025 NORCE
# SPDX-License-Identifier: GPL-3.0

"""
Script to run pyopmnearwell with different hysteresis models. It requires plopm:
https://github.com/cssr-tools/plopm
"""

import os
from mako.template import Template

command = ""
for name in ["nohysteresis", "Carlson", "Killough"]:
    mytemplate = Template(filename="co2.mako") 
    var = {"name": name}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"co2_{name}.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    command += f"pyopmnearwell -i co2_{name}.toml -o {name} -m single & "
command += "wait"
os.system(command)
command = ""
for quan in ["tcpu","msumlins","msumnewt","fgip","wbhp:inj0","fgir"]:
    command += f"plopm -i 'nohysteresis/CO2_NOHYSTERESIS Carlson/CO2_CARLSON Killough/CO2_KILLOUGH' -v {quan} &"
command += "wait"
os.system(command)