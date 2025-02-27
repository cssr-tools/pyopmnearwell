# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow for a random input variable
"""

import os
import math as mt
import numpy as np
from resdata.summary import Summary
from mako.template import Template
import matplotlib.pyplot as plt

np.random.seed(7)

GRATES = np.random.uniform(1000, 3000, 8) # Randomly sampled gas injection rate values
NPRUNS = 8 # Number of paralell runs (it should be limited by the number of your cpus)
DELETE = 1 # Set to 0 to no delete the simulation files (careful with your PC memmory)
FLOW = "flow"

mytemplate = Template(filename="co2eor.mako")
rate = []
ratio_oil_to_injected_volumes = []
for i, rate in enumerate(GRATES):
    var = {"flow": FLOW, "rate": rate}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"co2eor_{i}.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
for i in range(mt.floor(len(GRATES) / NPRUNS)):
    command = ""
    for j in range(NPRUNS):
        if DELETE == 1:
            command += f"pyopmnearwell -i co2eor_{NPRUNS*i+j}.toml -o co2eor_{NPRUNS*i+j} -g single -v 0 & "
        else:
            command += f"pyopmnearwell -i co2eor_{NPRUNS*i+j}.toml -o co2eor_{NPRUNS*i+j} -g single & "
    command += "wait"
    os.system(command)
    for j in range(NPRUNS):
        smspec = Summary(f"./co2eor_{NPRUNS*i+j}/CO2EOR_{NPRUNS*i+j}.SMSPEC")
        ratio_oil_to_injected_volumes.append(smspec["FOPT"].values[-1]/(smspec["FGIT"].values[-1]+smspec["FWIT"].values[-1]))
        if DELETE == 1:
            os.system(f"rm -rf co2eor_{NPRUNS*i+j} co2eor_{NPRUNS*i+j}.toml")
finished = NPRUNS * mt.floor(len(GRATES) / NPRUNS)
remaining = len(GRATES) - finished
command = ""
for i in range(remaining):
    if DELETE == 1:
        command += f"pyopmnearwell -i co2eor_{finished+i}.toml -o co2eor_{finished+i} -g single -v 0 & "
    else:
        command += f"pyopmnearwell -i co2eor_{finished+i}.toml -o co2eor_{finished+i} -g single & "
command += "wait"
os.system(command)
for i in range(remaining):
    smspec = Summary(f"./co2eor_{finished+i}/CO2EOR_{finished+i}.SMSPEC")
    ratio_oil_to_injected_volumes.append(smspec["FOPT"].values[-1]/(smspec["FGIT"].values[-1]+smspec["FWIT"].values[-1]))
    if DELETE == 1:
        os.system(f"rm -rf co2eor_{finished+i} co2eor_{finished+i}.toml")

np.save('rates', GRATES)
np.save('ratio_oil_to_injected_volumes', ratio_oil_to_injected_volumes)

fig, axis = plt.subplots()
axis.plot(
    GRATES,
    ratio_oil_to_injected_volumes,
    color="b",
    linestyle="",
    marker="*",
    markersize=5,
)
axis.set_ylabel(r"Recovered oil over injected volumes (gas + water) [-]", fontsize=12)
axis.set_xlabel(r"Gas injection rate [stb/day]", fontsize=12)
fig.savefig("ratio_oil_to_injected_volumes.png")