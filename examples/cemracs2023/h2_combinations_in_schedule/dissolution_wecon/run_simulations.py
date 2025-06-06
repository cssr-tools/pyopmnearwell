# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow for a random input variable
"""

import os
import math as mt
import numpy as np
import itertools
from resdata.summary import Summary
from mako.template import Template
import matplotlib.pyplot as plt

np.random.seed(7)

FLOW = "flow"
ECON = 0.95 #Minimum surface gas production rate (w.r.t gas prodcution rate, i.e., between 0 and 1)
NSCHED = 4  # Number of changues in the schedule
NPRUNS = 8 # Number of parallel simulations

nsimulations = 2**NSCHED #The number of inj/prod combinations given the number of changues in the injection (NSCHED)
schedules = [seq for seq in itertools.product("01", repeat=NSCHED)]
seq_string = ["".join(seq) for seq in itertools.product("01", repeat=NSCHED)]
for i, row in enumerate(schedules):
    schedules[i] = [int(column) for column in row]
ordered = np.argsort(np.array([sum(row) for row in schedules]))
schedules = np.array(schedules)[ordered]
names = []
for inx in ordered:
    names.append(seq_string[inx])
mytemplate = Template(filename="h2.mako")
fgit = []
fgpt = []
fgit_fgpt = []
for i, schedule in enumerate(schedules):
    var = {"flow": FLOW, "econ": ECON, "schedule": schedule}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"h2_{i}.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)

for i in range(mt.floor(nsimulations / NPRUNS)):
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
finished = NPRUNS*mt.floor(nsimulations / NPRUNS)
remaining = nsimulations - finished
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
np.save('schedules', schedules)
np.save('fgpt', fgpt)
np.save('fgit', fgit)
np.save('fgit-fgpt', fgit-fgpt)
np.save('names', np.array(names))

quantities = ["fgit", "fgpt", "fgit-fgpt"]
descriptions = ["Injected", "Produced", "Injected - Produced"]
for quantity, description in zip(quantities,descriptions): 
    fig, axis = plt.subplots()
    data = np.load(f'{quantity}.npy')
    axis.plot(
        range(len(schedules)),
        data,
        color='k',
        linestyle="",
        marker='*',
        markersize=5,
    )
    if len(schedules) <= 16:
        axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, len(schedules)), 2))
        axis.set_xticklabels(names, rotation=90)
    else:
        axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, 4), 2))
        axis.set_xticklabels([names[0],names[mt.floor(len(schedules)/4)],names[mt.floor(3*len(schedules)/4)],names[-1]], rotation=90)
    axis.set_ylabel(f"{description}" + r" H$_2$ [sm${^3}$]", fontsize=12)
    axis.set_xlabel(r"Sequence in the schedule [-]", fontsize=12)
    fig.savefig(f"{quantity}.png",bbox_inches='tight')
