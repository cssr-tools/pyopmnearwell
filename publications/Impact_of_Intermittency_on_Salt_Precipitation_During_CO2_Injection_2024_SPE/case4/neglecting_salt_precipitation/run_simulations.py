# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow
"""

import os
import math as mt
import numpy as np
import pandas as pd
import itertools
from resdata.summary import Summary
from resdata.resfile import ResdataFile
from resdata.grid import Grid
from mako.template import Template
import matplotlib.pyplot as plt

FLOW = "flow"
TPERIOD = 365 # Duration of one period in days
NSCHED = 3  # Number of changues in the schedule
NPRUNS = 10
REF_CO2_DENSITY = 1.86843  # CO2 reference density at surface conditions 
WAT_DEN_REF = 998.108 # Water reference density at surface conditions 
THRESHOLD_CO2_MASS = 100  # Threshold for the calculation of the CO2 gas (mass) location [kg]

scheduless = [seq for seq in itertools.product("01", repeat=2**NSCHED)]
seq_string = ["".join(seq) for seq in itertools.product("01", repeat=2**NSCHED)]
for i, row in enumerate(scheduless):
    scheduless[i] = [int(column) for column in row]
ordered = np.argsort(np.array([sum(row) for row in scheduless]))
scheduless = np.array(scheduless)[ordered]
namess = []
for inx in ordered:
    namess.append(seq_string[inx])
schedules = []
names = []
for i,row in enumerate(scheduless):
    if sum(row) == 2**(NSCHED-1) and row[0]>0:
        schedules.append(row)
        names.append(namess[i])
del schedules[10]
schedules.insert(0,[1,0,1,0,1,0,1,0])
del schedules[28]
schedules.insert(len(schedules),[1,1,1,1,0,0,0,0])
nsimulations = len(schedules)
names.remove('10101010')
names.remove('11110000')
names.insert(0, '10101010')
names.insert(len(names), '11110000')
mytemplate = Template(filename="co2.mako")
fgit= []
mass_salt = []
mass_co2_gas = []
mass_co2_dissolved = []
mass_co2_total = []
ratio_co2_dissolved_total = []
min_distance_to_boundary = []
wbhp, wbhpxyear = [], []
for i, schedule in enumerate(schedules):
    var = {"flow": FLOW, "tperiod": TPERIOD, "schedule": schedule}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"co2_{i}.txt",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)
for i in range(mt.floor(nsimulations / NPRUNS)):
    command = ""
    for j in range(NPRUNS):
        command += f"pyopmnearwell -i co2_{NPRUNS*i+j}.txt -o co2_{NPRUNS*i+j} -p off & " 
    command += 'wait'
    os.system(command)
    for j in range(NPRUNS):
        xcord = np.load(f"./co2_{NPRUNS*i+j}/output/xspace.npy")
        x_centers = 0.5 * (xcord[1:] + xcord[:-1])
        nx_cells = len(x_centers)
        zcord = np.load(f"./co2_{NPRUNS*i+j}/output/zspace.npy")
        z_centers = 0.5 * (zcord[1:] + zcord[:-1])
        nz_cells = len(z_centers)
        smspec = Summary(f"./co2_{NPRUNS*i+j}/output/CO2_{NPRUNS*i+j}.SMSPEC")
        unrst = ResdataFile(f"./co2_{NPRUNS*i+j}/output/CO2_{NPRUNS*i+j}.UNRST")
        init = ResdataFile(f"./co2_{NPRUNS*i+j}/output/CO2_{NPRUNS*i+j}.INIT")
        grid = Grid(f"./co2_{NPRUNS*i+j}/output/CO2_{NPRUNS*i+j}.EGRID")
        times = [
            (smspec.numpy_dates[i + 1] - smspec.numpy_dates[i])
            / np.timedelta64(1, "s")
            for i in range(len(smspec.numpy_dates) - 1)
        ]
        saltp = np.array(unrst.iget_kw("SGAS")[-1][:]) * 0. # no salt precipitation
        phiv = np.array(init.iget_kw("PORV")[0][:]) * (1.-saltp)
        sgas = np.array(unrst.iget_kw("SGAS")[-1][:])
        r_s = np.array(unrst.iget_kw("RSW")[-1][:])
        rhog = np.array(unrst.iget_kw("GAS_DEN")[-1][:])
        rhow = np.array(unrst.iget_kw("WAT_DEN")[-1][:])
        mass_salt.append(sum(saltp * np.array(init.iget_kw("PORV")[0][:])) * 2153 / 1000.)
        mass_co2_gas.append(sum(sgas * rhog * phiv))
        mass_co2_dissolved.append(sum(r_s * (1.0 - sgas) * phiv * rhow * REF_CO2_DENSITY / WAT_DEN_REF))
        mass_co2_total.append(mass_co2_gas[-1] + mass_co2_dissolved[-1])
        ratio_co2_dissolved_total.append(100 * mass_co2_dissolved[-1] / mass_co2_total[-1])
        wellp = smspec["WBHP:INJ0"].values
        wbhp.append(max(wellp))
        wbhpxyear.append(sum(times*(0.5*(wellp[1:]+wellp[:-1]))) / (86400.*365))
        # Handle the distance part
        indicator_mass = 1.0*((sgas * rhog * phiv) > THRESHOLD_CO2_MASS).reshape(nz_cells, nx_cells)
        max_distance_index = 0
        for row in indicator_mass:
            if max(row) > 0:
                max_distance_index = max(max_distance_index , len(row[::-1]) - pd.Series(row[::-1]).argmax() - 1)
        min_distance_to_boundary.append(xcord[1+max_distance_index])
        fgit.append(smspec["FGIT"].values[-1])
        os.system(f"rm -rf co2_{NPRUNS*i+j} co2_{NPRUNS*i+j}.txt")
finished = NPRUNS*mt.floor(nsimulations / NPRUNS)
remaining = nsimulations - finished
command = ""
for i in range(remaining):
    command += f"pyopmnearwell -i co2_{finished+i}.txt -o co2_{finished+i} -p off & " 
command += 'wait'
os.system(command)
for j in range(remaining):
    xcord = np.load(f"./co2_{finished+j}/output/xspace.npy")
    x_centers = 0.5 * (xcord[1:] + xcord[:-1])
    nx_cells = len(x_centers)
    zcord = np.load(f"./co2_{finished+j}/output/zspace.npy")
    z_centers = 0.5 * (zcord[1:] + zcord[:-1])
    nz_cells = len(z_centers)
    smspec = Summary(f"./co2_{finished+j}/output/CO2_{finished+j}.SMSPEC")
    unrst = ResdataFile(f"./co2_{finished+j}/output/CO2_{finished+j}.UNRST")
    init = ResdataFile(f"./co2_{finished+j}/output/CO2_{finished+j}.INIT")
    grid = Grid(f"./co2_{finished+j}/output/CO2_{finished+j}.EGRID")
    times = [
        (smspec.numpy_dates[i + 1] - smspec.numpy_dates[i])
        / np.timedelta64(1, "s")
        for i in range(len(smspec.numpy_dates) - 1)
    ]

    saltp = np.array(unrst.iget_kw("SGAS")[-1][:]) * 0. # no salt precipitation
    phiv = np.array(init.iget_kw("PORV")[0][:]) * (1.-saltp)
    r_s = np.array(unrst.iget_kw("RSW")[-1][:])
    rhog = np.array(unrst.iget_kw("GAS_DEN")[-1][:])
    rhow = np.array(unrst.iget_kw("WAT_DEN")[-1][:])
    mass_salt.append(sum(saltp * np.array(init.iget_kw("PORV")[0][:])) * 2153 / 1000.)
    mass_co2_gas.append(sum(sgas * rhog * phiv))
    mass_co2_dissolved.append(sum(r_s * (1.0 - sgas) * phiv * rhow * REF_CO2_DENSITY / WAT_DEN_REF))
    mass_co2_total.append(mass_co2_gas[-1] + mass_co2_dissolved[-1])
    ratio_co2_dissolved_total.append(100 * mass_co2_dissolved[-1] / mass_co2_total[-1])
    wellp = smspec["WBHP:INJ0"].values
    wbhp.append(max(wellp))
    wbhpxyear.append(sum(times*(0.5*(wellp[1:]+wellp[:-1]))) / (86400.*365))
    # Handle the distance part
    indicator_mass = 1.0*((sgas * rhog * phiv) > THRESHOLD_CO2_MASS).reshape(nz_cells, nx_cells)
    max_distance_index = 0
    for row in indicator_mass:
        if max(row) > 0:
            max_distance_index = max(max_distance_index , len(row[::-1]) - pd.Series(row[::-1]).argmax() - 1)
    min_distance_to_boundary.append(xcord[1+max_distance_index])
    fgit.append(smspec["FGIT"].values[-1])
    os.system(f"rm -rf co2_{finished+j} co2_{finished+j}.txt")

np.save('fgit', fgit)
np.save('rmdt', ratio_co2_dissolved_total)
np.save('maxwbhp', wbhp)
np.save('bhpxyear', wbhpxyear)
np.save('mindistance', min_distance_to_boundary)
np.save('names', names)
np.save('mass_salt', mass_salt)
np.save('schedules', schedules)

quantities = ["fgit", "rmdt", 'maxwbhp', 'mindistance', 'bhpxyear', 'mass_salt']
units = ["sm$^3$", "-", "bar", "m", "bar year", "t"]
descriptions = ["Injected CO2", "Ratio of dissolved CO2 to total", "Max well BHP", "CO2 distance to the well", "Well BHP integretaed over time", "Precipitated salt"]
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
    if len(schedules) <= 38:
        axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, len(schedules)), 2))
        axis.set_xticklabels(names, rotation=270)
    else:
        axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, 4), 2))
        axis.set_xticklabels([names[0][0:6]+'...',names[mt.floor(len(schedules)/4)],names[mt.floor(3*len(schedules)/4)][0:6]+'...',names[-1][0:6]+'...'], rotation=270)
    ylabel = description + f" [{units[j]}]"
    axis.set_ylabel(f"{ylabel}", fontsize=12)
    if quantity in ["fgit", "rmdt", 'mindistance']:
        axis.set_ylim(0)
    axis.set_xlabel(r"Sequence in the schedule [-]", fontsize=12)
    fig.savefig(f"{quantity}.png",bbox_inches='tight')
