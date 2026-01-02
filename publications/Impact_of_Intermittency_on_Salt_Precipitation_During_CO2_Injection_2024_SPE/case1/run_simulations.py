# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Case 1 in the publication. To generate Figure 6, this can be achieved using plopm by executing:
plopm -i a_nca_123_M_3kg_s/output/A_NCA_123_M_3KG_S -v saltp -z 0 -x '[0,20]' -c coolwarm
plopm -i a_nca_123_M_3kg_s/output/A_NCA_123_M_3KG_S -v sgas -z 0 -x '[0,20]'
plopm -i a_nca_123_M_3kg_s/output/A_NCA_123_M_3KG_S -v pressure -z 0 -x '[0,20]' -c seismic
plopm -i . -v saltp -x '[0,20]' -s :,1,20 -lw 3,3,3,3,3,3
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
        f"{case}_nca_{n_ca:.0f}_M_{qrate}kg_s.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
    command += f"pyopmnearwell -i {case}_nca_{n_ca:.0f}_M_{qrate}kg_s.toml -o {case}_nca_{n_ca:.0f}_M_{qrate}kg_s & "
command += "wait"
os.system(command)
