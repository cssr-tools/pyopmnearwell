# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow for a random input variable
"""

import os

import matplotlib.pyplot as plt
import numpy as np
from resdata.summary import Summary
from mako.template import Template

npoints, npruns = 20, 5
tmin, tmax = 0, 30
times = np.random.uniform(tmin, tmax, npoints)

FLOW = "/Users/dmar/Github/opm/build/opm-simulators/bin/flow"
FLAGS = (
    " --linear-solver-reduction=1e-5 --relaxed-max-pv-fraction=0"
    + " --enable-drift-compensation=0 --newton-max-iterations=50"
    + " --newton-min-iterations=5 --tolerance-mb=1e-7 --tolerance-wells=1e-5"
    + " --relaxed-well-flow-tol=1e-5 --use-multisegment-well=false --enable-tuning=true"
    + " --enable-opm-rst-file=true --linear-solver=cprw --enable-well-operability-check=false"
    + " --min-time-step-before-shutting-problematic-wells-in-days=1e-99"
)

mytemplate = Template(filename="RESERVOIR.mako")
time = []
fgpt = []
for i, time in enumerate(times):
    var = {"time": time}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"RESERVOIR{i}.DATA",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)

for i in range(round(npoints / npruns)):
    os.system(
        f"{FLOW}"
        + f" RESERVOIR{npruns*i}.DATA --output-dir=results{npruns*i} {FLAGS} & "
        f"{FLOW}"
        + f" RESERVOIR{npruns*i+1}.DATA --output-dir=results{npruns*i+1} {FLAGS} & "
        f"{FLOW}"
        + f" RESERVOIR{npruns*i+2}.DATA --output-dir=results{npruns*i+2} {FLAGS} & "
        f"{FLOW}"
        + f" RESERVOIR{npruns*i+3}.DATA --output-dir=results{npruns*i+3} {FLAGS} & "
        f"{FLOW}"
        + f" RESERVOIR{npruns*i+4}.DATA --output-dir=results{npruns*i+4} {FLAGS} & wait"
    )
    for j in range(npruns):
        smspec = Summary(f"results{npruns*i+j}/RESERVOIR{npruns*i+j}.SMSPEC")
        fgpt.append(smspec["FGPT"].values[-1])
        os.system(f"rm -rf results{npruns*i+j} RESERVOIR{npruns*i+j}.DATA")

fig, axis = plt.subplots()
axis.plot(
    times,
    fgpt,
    color="b",
    linestyle="",
    marker="*",
    markersize=5,
)
axis.set_ylabel("Recovered H2 [sm3]", fontsize=12)
axis.set_xlabel("Time of injection [days]", fontsize=12)
fig.savefig("fgpt.png")
