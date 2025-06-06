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

FLOW = "flow"
TPERIODI = 10 #Duration of the injection period in days
TPERIODP = 5 #Duration of the injection period in days
QI = 10000 # Injection rate [kg/day]
QP = 20000 # Production rate [kg/day]
NSCHED = 10  # Number of cycles (injection-withdrawal)
NPRUNS = 8 # Number of parallel simulations

TPERIOD = TPERIODI + TPERIODP
times = np.linspace(TPERIOD, TPERIOD * NSCHED, NSCHED)
mytemplate = Template(filename="h2.mako")
time, fgit, fgpt, fgit_fgpt, rfac = [], [], [], [], []
for i, time in enumerate(times):
    var = {"flow": FLOW, "tperiodi": TPERIODI, "tperiodp": TPERIODP, "qi": QI, "qp": QP, "time": time}
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
        rfac.append(100.*smspec["FGPT"].values[-1]/smspec["FGIT"].values[-1])
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
    rfac.append(100.*smspec["FGPT"].values[-1]/smspec["FGIT"].values[-1])
    os.system(f"rm -rf h2_{finished+i} h2_{finished+i}.toml")

fgpt = np.array(fgpt)
fpit = np.array(fgit)
np.save('times', times)
np.save('fgpt', fgpt)
np.save('fgit', fgit)
np.save('fgit-fgpt', fgit-fgpt)
np.save('rfac', rfac)

quantities = ["fgit", "fgpt", "fgit-fgpt", "rfac"]
units = [r" H$_2$ [sm${^3}$]", r" H$_2$ [sm${^3}$]", r" H$_2$ [sm${^3}$]", "[%]"]
descriptions = ["Injected", "Produced", "Injected - Produced", "Recovery factor"]
for i, (quantity, description) in enumerate(zip(quantities,descriptions)): 
    fig, axis = plt.subplots()
    data = np.load(f'{quantity}.npy')
    axis.plot(
        range(1,len(times)+1),
        data,
        color='k',
        linestyle="",
        marker='*',
        markersize=5,
    )
    axis.set_ylabel(f"{description}" + units[i], fontsize=12)
    axis.set_xlabel("Injection-withdrawal cycle [#]", fontsize=10)
    axis.set_xticks(range(1,len(times)+1))
    if quantity == "rfac":
        axis.set_ylim(0)
    fig.savefig(f"{quantity}.png",bbox_inches='tight')