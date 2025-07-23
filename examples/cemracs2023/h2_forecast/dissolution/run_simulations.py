# SPDX-FileCopyrightText: 2023-2025, NORCE Research AS
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

FLOW = "flow"
ECON = 0 #Minimum surface gas production rate (w.r.t gas prodcution rate, i.e., between 0 and 1)
TPERIOD = 7 #Duration of one period in days
NSCHED = 10  # Number of changues in the schedule
NSAMPLES = 0  # Number of samples in a period (TPERIOD, 0 samples correspond to only simulating the beguining and end of the period)
NPRUNS = 8 # Number of parallel simulations

times = np.linspace(0, TPERIOD * NSCHED, (NSAMPLES + 1) * NSCHED + 1)
mytemplate = Template(filename="h2.mako")
time, fgit, fgpt, fgit_fgpt = [], [], [], []
for i, time in enumerate(times):
    var = {"flow": FLOW, "econ": ECON, "tperiod": TPERIOD, "time": time}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"h2_{i}.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
for i in range(mt.floor(len(times) / NPRUNS)):
    command = ""
    for j in range(NPRUNS):
        command += f"pyopmnearwell -i h2_{NPRUNS*i+j}.toml -o h2_{NPRUNS*i+j} & " 
    command += 'wait'
    os.system(command)
    for j in range(NPRUNS):
        smspec = Summary(f"./h2_{NPRUNS*i+j}/output/H2_{NPRUNS*i+j}.SMSPEC")
        fgit.append(smspec["FGIT"].values[-1])
        fgpt.append(smspec["FGPT"].values[-1])
        fgit_fgpt.append(smspec["FGIT"].values[-1] - smspec["FGPT"].values[-1])
        os.system(f"rm -rf h2_{NPRUNS*i+j} h2_{NPRUNS*i+j}.toml")
finished = NPRUNS*mt.floor(len(times) / NPRUNS)
remaining = len(times) - finished
command = ""
for i in range(remaining):
    command += f"pyopmnearwell -i h2_{finished+i}.toml -o h2_{finished+i} & " 
command += 'wait'
os.system(command)
for i in range(remaining):
    smspec = Summary(f"./h2_{finished+i}/output/H2_{finished+i}.SMSPEC")
    fgit.append(smspec["FGIT"].values[-1])
    fgpt.append(smspec["FGPT"].values[-1])
    fgit_fgpt.append(smspec["FGIT"].values[-1] - smspec["FGPT"].values[-1])
    os.system(f"rm -rf h2_{finished+i} h2_{finished+i}.toml")

fgpt = np.array(fgpt)
fpit = np.array(fgit)
np.save('times', times)
np.save('fgpt', fgpt)
np.save('fgit', fgit)
np.save('fgit-fgpt', fgit-fgpt)

quantities = ["fgit", "fgpt", "fgit-fgpt"]
descriptions = ["Injected", "Produced", "Injected - Produced"]
for quantity, description in zip(quantities,descriptions): 
    fig, axis = plt.subplots()
    data = np.load(f'{quantity}.npy')
    axis.plot(
        times,
        data,
        color='k',
        linestyle="",
        marker='*',
        markersize=5,
    )
    axis.set_ylabel(f"{description}" + r" H$_2$ [sm${^3}$]", fontsize=12)
    axis.set_xlabel("Time (after the 365 d inj + 90 d stop) to assess the operation [d]", fontsize=10)
    fig.savefig(f"{quantity}.png",bbox_inches='tight')
