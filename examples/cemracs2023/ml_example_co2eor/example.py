# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow for a random input variable
"""

import os
import numpy as np
from resdata.summary import Summary
from mako.template import Template
import matplotlib.pyplot as plt

np.random.seed(7)

npoints, npruns = 5, 5
rmin, rmax = 1000, 3000
rates = np.random.uniform(rmin, rmax, npoints)

FLOW = "/Users/dmar/Github/opm/build/opm-simulators/bin/flow"

mytemplate = Template(filename="co2eor.mako")
rate = []
ratio_oil_to_injected_volumes = []
for i, rate in enumerate(rates):
    var = {"flow": FLOW, "rate": rate}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"co2eor_{i}.txt",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)

for i in range(round(npoints / npruns)):
    os.system(
        f"pyopmnearwell -i co2eor_{npruns*i}.txt -o co2eor_{npruns*i} -p '' & "
        + f"pyopmnearwell -i co2eor_{npruns*i+1}.txt -o co2eor_{npruns*i+1} -p '' & "
        + f"pyopmnearwell -i co2eor_{npruns*i+2}.txt -o co2eor_{npruns*i+2} -p '' & "
        + f"pyopmnearwell -i co2eor_{npruns*i+3}.txt -o co2eor_{npruns*i+3} -p '' & "
        + f"pyopmnearwell -i co2eor_{npruns*i+4}.txt -o co2eor_{npruns*i+4} -p '' & wait"
    )
    for j in range(npruns):
        smspec = Summary(f"./co2eor_{npruns*i+j}/output/CO2EOR_{npruns*i+j}.SMSPEC")
        ratio_oil_to_injected_volumes.append(smspec["FOPT"].values[-1]/(smspec["FGIT"].values[-1]+smspec["FWIT"].values[-1]))
        os.system(f"rm -rf co2eor_{npruns*i+j} co2eor_{npruns*i+j}.txt")

np.save('rates', rates)
np.save('ratio_oil_to_injected_volumes', ratio_oil_to_injected_volumes)

fig, axis = plt.subplots()
axis.plot(
    rates,
    ratio_oil_to_injected_volumes,
    color="b",
    linestyle="",
    marker="*",
    markersize=5,
)
axis.set_ylabel(r"Recovered oil over injected volumes (gas + water) [-]", fontsize=12)
axis.set_xlabel(r"Gas injection rate [stb/day]", fontsize=12)
fig.savefig("ratio_oil_to_injected_volumes.png")
