# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow for a random input variable
"""

import os
import numpy as np
from ecl.summary import EclSum
from mako.template import Template
import matplotlib.pyplot as plt

np.random.seed(7)

npoints, npruns = 30, 5
tmin, tmax = 0, 365
times = np.random.uniform(tmin, tmax, npoints)

FLOW = "/Users/dmar/Github/opm/build/opm-simulators/bin/flow"
FLAGS = (
    " --linear-solver-reduction=1e-5 --relaxed-max-pv-fraction=0"
    + " --ecl-enable-drift-compensation=0 --newton-max-iterations=50"
    + " --newton-min-iterations=5 --tolerance-mb=1e-7 --tolerance-wells=1e-5"
    + " --relaxed-well-flow-tol=1e-5 --use-multisegment-well=false --enable-tuning=true"
    + " --enable-opm-rst-file=true --linear-solver=cprw --enable-well-operability-check=false"
    + " --min-time-step-before-shutting-problematic-wells-in-days=1e-99"
)

mytemplate = Template(filename="RESERVOIR.mako")
time = []
ratio_fgpt_to_fgit = []
fgit = []
wbhp = []
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
        smspec = EclSum(f"results{npruns*i+j}/RESERVOIR{npruns*i+j}.SMSPEC")
        ratio_fgpt_to_fgit.append(smspec["FGPT"].values[-1]/smspec["FGIT"].values[-1])
        wbhp.append(max(smspec["WBHP:PRO0"].values))
        fgit.append(smspec["FGIT"].values[-1])
        os.system(f"rm -rf results{npruns*i+j} RESERVOIR{npruns*i+j}.DATA")

np.save('times', times)
np.save('ratio_fgpt_to_fgit', ratio_fgpt_to_fgit)
np.save('wbhp', wbhp)

fig, axis = plt.subplots()
axis.plot(
    times,
    ratio_fgpt_to_fgit,
    color="b",
    linestyle="",
    marker="*",
    markersize=5,
)
axis.set_ylabel(r"Recovered H$_2$ over injected H$_2$ [-]", fontsize=12)
axis.set_xlabel(r"Time of injected H${_2}$ [d]", fontsize=12)
fig.savefig("ratio_fgpt_to_fgit.png")

fig, axis = plt.subplots()
axis.plot(
    times,
    wbhp,
    color="b",
    linestyle="",
    marker="*",
    markersize=5,
)
axis.set_ylabel("Bhp [Bar]", fontsize=12)
axis.set_xlabel(r"Time of injected H${_2}$ [d]", fontsize=12)
fig.savefig("pbhp.png")
