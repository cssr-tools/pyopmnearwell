# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os
from mako.template import Template

QRATE = [3, 5, 10, 15, 20, 30]
CASES = ["a", "b", "c", "d", "e", "f"]

height = 100
phi = 0.1
perm = 101.3 / 1.01324997e15
rhog = 636
m_u = 4.8e-5
p_e = 1.96e3
l_c = 1
r_d = 0.15

os.system("rm -rf compare")
mytemplate = Template(filename="salt.mako")
command = ""
for i, (case, qrate) in enumerate(zip(CASES, QRATE)):
    n_ca = (m_u * qrate * l_c) / (rhog * phi * perm * p_e * height * 2 * 3.1416 * r_d)
    var = {"qrate": qrate}
    filledtemplate = mytemplate.render(**var)
    os.system(f"rm -rf {case}_nca_{n_ca:.0f}_M_{qrate}kg_s")
    with open(
        f"{case}_nca_{n_ca:.0f}_M_{qrate}kg_s.txt",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    command += f"pyopmnearwell -i {case}_nca_{n_ca:.0f}_M_{qrate}kg_s.txt -o {case}_nca_{n_ca:.0f}_M_{qrate}kg_s -p opm & "
command += "wait"
os.system(command)
os.system("pyopmnearwell -c compare -m saltprec -p opm")
