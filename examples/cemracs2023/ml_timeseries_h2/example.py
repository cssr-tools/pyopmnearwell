# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow for a random input variable
"""

import os
import math as mt
import numpy as np
from ecl.summary import EclSum
from mako.template import Template
import matplotlib.pyplot as plt

np.random.seed(7)

FLOW = "/Users/dmar/Github/opm/build/opm-simulators/bin/flow"
ECON = 0.95 #Minimum surface gas production rate (w.r.t gas prodcution rate, i.e., between 0 and 1)

nsimulations, npruns = 57, 5
tmin, tmax = 0, 98  # Time to evaluate the ratio of produce H2 to injected H2 [70 days of cyclic as in the paper plus 4 more cycles (28 days) to assess the ml]
times = np.linspace(tmin, tmax, nsimulations)
mytemplate = Template(filename="h2.mako")
time = []
fgit = []
fgpt = []
fgit_fgpt = []
for i, time in enumerate(times):
    var = {"flow": FLOW, "econ": ECON, "time": time}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"h2_{i}.txt",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
for i in range(mt.floor(nsimulations / npruns)):
    os.system(
        f"pyopmnearwell -i h2_{npruns*i}.txt -o h2_{npruns*i} -p '' & "
        + f"pyopmnearwell -i h2_{npruns*i+1}.txt -o h2_{npruns*i+1} -p '' & "
        + f"pyopmnearwell -i h2_{npruns*i+2}.txt -o h2_{npruns*i+2} -p '' & "
        + f"pyopmnearwell -i h2_{npruns*i+3}.txt -o h2_{npruns*i+3} -p '' & "
        + f"pyopmnearwell -i h2_{npruns*i+4}.txt -o h2_{npruns*i+4} -p '' & wait"
    )
    for j in range(npruns):
        smspec = EclSum(f"./h2_{npruns*i+j}/output/H2_{npruns*i+j}.SMSPEC")
        fgit_fgpt.append(smspec["FGIT"].values[-1] - smspec["FGPT"].values[-1])
        fgit.append(smspec["FGIT"].values[-1])
        fgpt.append(smspec["FGPT"].values[-1])
        os.system(f"rm -rf h2_{npruns*i+j} h2_{npruns*i+j}.txt")
finished = npruns*mt.floor(nsimulations / npruns)
remaining = nsimulations - finished
for i in range(remaining):
    os.system(
        f"pyopmnearwell -i h2_{finished+i}.txt -o h2_{finished+i} -p '' & wait"
    )
    smspec = EclSum(f"./h2_{finished+i}/output/H2_{finished+i}.SMSPEC")
    fgit_fgpt.append(smspec["FGIT"].values[-1] - smspec["FGPT"].values[-1])
    fgit.append(smspec["FGIT"].values[-1])
    fgpt.append(smspec["FGPT"].values[-1])
    os.system(f"rm -rf h2_{finished+i} h2_{finished+i}.txt")

np.save('times', 365 + 90 + times)
np.save('fgpt', fgpt)
np.save('fgit', fgit)

fig, axis = plt.subplots()
axis.plot(
    365 + 90 + times,
    fgit,
    color="b",
    linestyle="",
    marker="*",
    markersize=5,
)
axis.set_ylabel(r"Injected H$_2$ [sm${^3}$]", fontsize=12)
axis.set_xlabel(r"Time to assess the operation [d]", fontsize=12)
fig.savefig("fgit.png")

fig, axis = plt.subplots()
axis.plot(
    365 + 90 + times,
    fgpt,
    color="b",
    linestyle="",
    marker="*",
    markersize=5,
)
axis.set_ylabel(r"Produced H$_2$ [sm${^3}$]", fontsize=12)
axis.set_xlabel(r"Time to assess the operation [d]", fontsize=12)
fig.savefig("fgpt.png")

fig, axis = plt.subplots()
axis.plot(
    365 + 90 + times,
    fgit_fgpt,
    color="b",
    linestyle="",
    marker="*",
    markersize=5,
)
axis.set_ylabel(r"Difference H$_2$ injected and produced [sm${^3}$]", fontsize=12)
axis.set_xlabel(r"Time to assess the operation [d]", fontsize=12)
fig.savefig("fgit_fgpt.png")
