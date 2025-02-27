# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow for a random input variable
"""

import os
import math as mt
import argparse
import numpy as np
from resdata.summary import Summary
from mako.template import Template
import matplotlib.pyplot as plt

np.random.seed(7)

parser = argparse.ArgumentParser(description="Main script to plot the results")
parser.add_argument(
    "-f",
    "--flow",
    default="flow",
)
parser.add_argument(
    "-q",
    "--qratew",
    default=15000.,
)
parser.add_argument(
    "-g",
    "--qrateg",
    default=15000.,
)
parser.add_argument(
    "-t",
    "--tperiod",
    default=30,
)
parser.add_argument(
    "-n",
    "--nsched",
    default=8,
)
parser.add_argument(
    "-p",
    "--parallel",
    default=5,
)
cmdargs = vars(parser.parse_known_args()[0])

FLOW = cmdargs["flow"]
QRATEW = float(cmdargs["qratew"])
QRATEG = float(cmdargs["qrateg"])
TPERIOD = int(cmdargs["tperiod"])
NSCHED = int(cmdargs["nsched"])
NPRUNS = int(cmdargs["parallel"])

STB_BBL = 5.6146e-3

nsimulations = NSCHED #The number of inj/prod combinations given the number of changues in the injection (NSCHED) 15*128/30 = 64
nperiods = 2**NSCHED
schedules = []
seq_string = []
for i in range(nsimulations):
    schedules.append([])
    schedule = []
    seq0 = ''
    seq1 = ''
    for j in range(2**i):
        seq0 += '0'
        schedule.append(0)
    for j in range(len(seq0)):
        seq0 += '1'
        schedule.append(1)
    for _ in range(mt.floor(nperiods/(len(seq0)))):
        seq1 += seq0
        schedules[-1].extend(schedule)
    seq_string.append(seq1)

names = seq_string

mytemplate = Template(filename="co2eor.mako")
fvit = []
fvpt = []
fopt = []
fnpt = []
fnit = []
fvit_fvpt = []
fnit_fnpt = []
for i, schedule in enumerate(schedules):
    var = {"flow": FLOW, "qratew": QRATEW, "qrateg": QRATEG, "tperiod": TPERIOD, "schedule": schedule}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"co2eor_{i}.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
for i in range(mt.floor(nsimulations / NPRUNS)):
    command = ""
    for j in range(NPRUNS):
        command += f"pyopmnearwell -i co2eor_{NPRUNS*i+j}.toml -o co2eor_{NPRUNS*i+j} -g single -v 0 & " 
    command += 'wait'
    os.system(command)
    for j in range(NPRUNS):
        smspec = Summary(f"./co2eor_{NPRUNS*i+j}/CO2EOR_{NPRUNS*i+j}.SMSPEC")
        fvit.append(smspec["FWIT"].values[-1]+smspec["FGIT"].values[-1] / STB_BBL)
        fvpt.append(smspec["FOPT"].values[-1]+smspec["FWPT"].values[-1] + smspec["FGPT"].values[-1] / STB_BBL)
        fvit_fvpt.append(fvit[-1]-fvpt[-1])
        fnit.append(smspec["FNIT"].values[-1])
        fnpt.append(smspec["FNPT"].values[-1])
        fopt.append(smspec["FOPT"].values[-1])
        fnit_fnpt.append(fnit[-1]-fnpt[-1])
        os.system(f"rm -rf co2eor_{NPRUNS*i+j} co2eor_{NPRUNS*i+j}.toml")
finished = NPRUNS*mt.floor(nsimulations / NPRUNS)
remaining = nsimulations - finished
command = ""
for i in range(remaining):
    command += f"pyopmnearwell -i co2eor_{finished+i}.toml -o co2eor_{finished+i} -g single -v 0 & " 
command += 'wait'
os.system(command)
for j in range(remaining):
    smspec = Summary(f"./co2eor_{finished+j}/CO2EOR_{finished+j}.SMSPEC")
    fvit.append(smspec["FWIT"].values[-1]+smspec["FGIT"].values[-1] / STB_BBL)
    fvpt.append(smspec["FOPT"].values[-1]+smspec["FWPT"].values[-1] + smspec["FGPT"].values[-1] / STB_BBL)
    fvit_fvpt.append(fvit[-1]-fvpt[-1])
    fnit.append(smspec["FNIT"].values[-1])
    fnpt.append(smspec["FNPT"].values[-1])
    fopt.append(smspec["FOPT"].values[-1])
    fnit_fnpt.append(fnit[-1]-fnpt[-1])
    os.system(f"rm -rf co2eor_{finished+j} co2eor_{finished+j}.toml")

fvpt = np.array(fvpt)
fvit = np.array(fvit)
fnpt = np.array(fnpt)
fnit = np.array(fnit)
fopt = np.array(fopt)
np.save('schedules', schedules)
np.save('fvpt', fvpt)
np.save('fvit', fvit)
np.save('fvit-fvpt', fvit-fvpt)
np.save('fnpt', fnpt)
np.save('fnit', fnit)
np.save('fnit-fnpt', fnit-fnpt)
np.save('1-fvpt_fvit', (fvit-fvpt) / fvit)
np.save('fopt', fopt)
np.save('names', np.array(names))

quantities = ["fvit", "fvpt", "fvit-fvpt", "fnit", "fnpt", "fnit-fnpt", "1-fvpt_fvit", "fopt"]
units = ["stb", "stb", "stb","stb", "stb", "stb", "-", "stb"]
descriptions = ["Injected", "Produced", "Injected - Produced", "Injected CO2", "Produced CO2", "Injected - Produced CO2", "(Injected - Produced) / Injected", "Produced OIL"]
for j,(quantity, description) in enumerate(zip(quantities,descriptions)):
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
    if len(schedules) <= 27:
        axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, len(schedules)), 2))
        axis.set_xticklabels([name[0:6]+'...' for name in names], rotation=270)
    else:
        axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, 4), 2))
        axis.set_xticklabels([names[0][0:6]+'...',names[mt.floor(len(schedules)/4)][0:6]+'...',names[mt.floor(3*len(schedules)/4)],names[-1][0:6]+'...'], rotation=270)
    ylabel = description + f"[{units[j]}]"
    axis.set_ylabel(f"{ylabel}", fontsize=12)
    axis.set_ylim(0)
    axis.set_xlabel(r"Sequence in the schedule [-]", fontsize=12)
    fig.savefig(f"{quantity}.png",bbox_inches='tight')
