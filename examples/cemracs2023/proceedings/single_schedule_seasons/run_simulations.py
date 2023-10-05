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

FLOW = "flow"
TPERIODI = 10 #Duration of the injection period in days
TPERIODP = 5 #Duration of the injection period in days
TPERIODS = 20 #Duration of the shut-in period in days
QI = 40000 # Injection rate [kg/day]
QP = 100000 # Production rate [kg/day]
NSCHED = 20  # Number of cycles (injection-withdrawal)
NSEASON = 10  # Number of seasons
NPRUNS = 1 # Number of parallel simulations

TPERIOD = TPERIODI + TPERIODP + TPERIODS
times = np.linspace(TPERIOD, TPERIOD * NSCHED, NSCHED)
times = np.append(times, 0)
mytemplate = Template(filename="h2.mako")
for k in range(NSEASON):
    for i, time in enumerate(times):
        if i+k*len(times) == mt.floor(NSEASON*len(times))-1: 
            var = {"flow": FLOW, "tperiodi": TPERIODI, "tperiodp": TPERIODP, "tperiods": TPERIODS, "qi": QI, "qp": QP, "time": time, "timep": times[-2], "nseason": k+1}
            filledtemplate = mytemplate.render(**var)
            with open(
                f"h2_{i+k*len(times)}.txt",
                "w",
                encoding="utf8",
            ) as file:
                file.write(filledtemplate)
#for i in range(mt.floor(NSEASON*len(times) / NPRUNS)):
for i in range(mt.floor(NSEASON*len(times) / NPRUNS)-1, mt.floor(NSEASON*len(times) / NPRUNS)):
    command = ""
    for j in range(NPRUNS):
        command += f"pyopmnearwell -i h2_{NPRUNS*i+j}.txt -o h2_{NPRUNS*i+j} -p '' & " 
    command += 'wait'
    os.system(command)
    for j in range(NPRUNS):
        smspec = EclSum(f"./h2_{NPRUNS*i+j}/output/H2_{NPRUNS*i+j}.SMSPEC")
        times = smspec.dates
        fgit = smspec["FGIT"].values
        fgpt = smspec["FGPT"].values
        fgit_fgpt = smspec["FGIT"].values - smspec["FGPT"].values
        rfac = 100.*smspec["FGPT"].values/smspec["FGIT"].values
        #os.system(f"rm -rf h2_{NPRUNS*i+j} h2_{NPRUNS*i+j}.txt")

fgpt = np.array(fgpt)
fpit = np.array(fgit)
#np.save('times', times)
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
        times ,
        data,
        color='k',
        linestyle="",
        marker='*',
        markersize=5,
    )
    axis.set_ylabel(f"{description}" + units[i], fontsize=12)
    axis.set_xlabel("Injection-withdrawal cycle [#]", fontsize=10)
    if quantity == "rfac":
        axis.set_ylim(0)
    fig.savefig(f"{quantity}.png",bbox_inches='tight')
