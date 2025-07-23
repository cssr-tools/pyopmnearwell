# SPDX-FileCopyrightText: 2023-2025, NORCE Research AS
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

npoints, npruns = 30, 5
tmin, tmax = 0, 365
times = np.random.uniform(tmin, tmax, npoints)

FLOW = "flow"

mytemplate = Template(filename="h2.mako")
time = []
ratio_fgpt_to_fgit = []
fgit = []
wbhp = []
for i, time in enumerate(times):
    var = {"flow": FLOW, "time": time}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"h2_{i}.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)

for i in range(round(npoints / npruns)):
    os.system(
        f"pyopmnearwell -i h2_{npruns*i}.toml -o h2_{npruns*i} & "
        + f"pyopmnearwell -i h2_{npruns*i+1}.toml -o h2_{npruns*i+1} & "
        + f"pyopmnearwell -i h2_{npruns*i+2}.toml -o h2_{npruns*i+2} & "
        + f"pyopmnearwell -i h2_{npruns*i+3}.toml -o h2_{npruns*i+3} & "
        + f"pyopmnearwell -i h2_{npruns*i+4}.toml -o h2_{npruns*i+4} & wait"
    )
    for j in range(npruns):
        smspec = Summary(f"./h2_{npruns*i+j}/output/H2_{npruns*i+j}.SMSPEC")
        ratio_fgpt_to_fgit.append(smspec["FGPT"].values[-1]/smspec["FGIT"].values[-1])
        wbhp.append(max(smspec["WBHP:PRO0"].values))
        fgit.append(smspec["FGIT"].values[-1])
        os.system(f"rm -rf h2_{npruns*i+j} h2_{npruns*i+j}.toml")

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
