# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow for a random input variable
"""

import os
import math as mt
import numpy as np
import pandas as pd
from resdata.summary import Summary
from resdata.resfile import ResdataFile
from mako.template import Template
import matplotlib.pyplot as plt

np.random.seed(7)

FLOW = "flow"
TPERIODI = 10 #Duration of the injection period in days
TPERIODP = 5 #Duration of the production period in days
TPERIODS = 20 #Duration of the shut-in period in days
TPERIODE = 30 #Duration of the production at the end of the season
TSAMPLE = 5 #Size of the time step to print the results in days
QI = 20 # Injection rate [kg/day]
QP = 40 # Production rate [kg/day]
BHP = 3e6 # Minimum BHP for the producer [Pa]
NSCHED = 5  # Number of cycles (injection-withdrawal)
NSEASON = 7  # Number of seasons
NPRUNS = 1 # Number of parallel simulations

TPERIOD = TPERIODI + TPERIODP + TPERIODS
times = np.linspace(TPERIOD, TPERIOD * NSCHED, NSCHED)
times = np.append(times, 0)
rst_seconds = np.array([86400*TSAMPLE*(i+1) for i in range(mt.floor(NSEASON*(times[-2]+TPERIODE)/TSAMPLE))])
mytemplate = Template(filename="h2.mako")
for k in range(NSEASON):
    for i, time in enumerate(times):
        if i+k*len(times) == mt.floor(NSEASON*len(times))-1: 
            var = {"flow": FLOW, "tsample": TSAMPLE, "tperiode": TPERIODE, "tperiodi": TPERIODI, "tperiodp": TPERIODP, "tperiods": TPERIODS, "bhp": BHP, "qi": QI, "qp": QP, "time": time, "timep": times[-2], "nseason": k+1}
            filledtemplate = mytemplate.render(**var)
            with open(
                f"h2_{i+k*len(times)}.txt",
                "w",
                encoding="utf8",
            ) as file:
                file.write(filledtemplate)
for n in range(mt.floor(NSEASON*len(times) / NPRUNS)-1, mt.floor(NSEASON*len(times) / NPRUNS)):
    command = ""
    for j in range(NPRUNS):
        command += f"pyopmnearwell -i h2_{NPRUNS*n+j}.txt -o h2_{NPRUNS*n+j} -p '' & " 
    command += 'wait'
    os.system(command)
    for j in range(NPRUNS):
        smspec = Summary(f"./h2_{NPRUNS*n+j}/output/H2_{NPRUNS*n+j}.SMSPEC")
        rst = ResdataFile(f"./h2_{NPRUNS*n+j}/output/H2_{NPRUNS*n+j}.UNRST")
        smsp_report_step = smspec.report_step
        report_time = rst.dates
        smsp_seconds = [(smspec.numpy_dates[i + 1] - smspec.numpy_dates[i]) / np.timedelta64(1, "s") for i in range(len(smspec.numpy_dates) - 1)]
        for i in range(len(smsp_seconds) - 1):
            smsp_seconds[i + 1] += smsp_seconds[i]
        smsp_rst = [pd.Series(abs(smsp_seconds - time)).argmin() for time in rst_seconds]
        times = np.insert(rst_seconds, 0, 0) / 86400.
        fgit = [0]
        fgpt = [0]
        fgit_fgpt = [0]
        rfac = [0]
        for indx in smsp_rst:
            fgit.append(smspec["FGIT"].values[indx])
            fgpt.append(smspec["FGPT"].values[indx])
            fgit_fgpt.append(smspec["FGIT"].values[indx] - smspec["FGPT"].values[indx])
            rfac.append(100.*smspec["FGPT"].values[indx]/smspec["FGIT"].values[indx])
        #os.system(f"rm -rf h2_{NPRUNS*i+j} h2_{NPRUNS*i+j}.txt")
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
        times ,
        data,
        color='k',
        linestyle="",
        marker='*',
        markersize=5,
    )
    axis.set_ylabel(f"{description}" + units[i], fontsize=12)
    axis.set_xlabel("Days [#]", fontsize=10)
    if quantity == "rfac":
        axis.set_ylim(0)
    fig.savefig(f"{quantity}.png",bbox_inches='tight')
