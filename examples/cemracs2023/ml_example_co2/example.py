# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow for a random input variable
"""

import os
import numpy as np
import pandas as pd
from resdata.grid import Grid
from resdata.resfile import ResdataFile
from resdata.summary import Summary
from mako.template import Template
import matplotlib.pyplot as plt

np.random.seed(7)

npoints, npruns = 20, 5
tmin, tmax = 0, 365
times = np.random.uniform(tmin, tmax, npoints)

FLOW = "/Users/dmar/Github/opm/build/opm-simulators/bin/flow"
REF_CO2_DENSITY = 1.86843  # CO2 reference density at surface conditions 
THRESHOLD_CO2_MASS = 1000  # Threshold for the calculation of the CO2 gas (mass) location [kg]

mytemplate = Template(filename="co2.mako")
time = []
mass_co2_gas = []
mass_co2_dissolved = []
mass_co2_total = []
ratio_co2_dissolved_total = []
min_distance_to_boundary = []
wbhp = []
for i, time in enumerate(times):
    var = {"flow": FLOW, "time": time}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"co2_{i}.txt",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)

for i in range(round(npoints / npruns)):
    os.system(
        f"pyopmnearwell -i co2_{npruns*i}.txt -o co2_{npruns*i} -p '' & "
        + f"pyopmnearwell -i co2_{npruns*i+1}.txt -o co2_{npruns*i+1} -p '' & "
        + f"pyopmnearwell -i co2_{npruns*i+2}.txt -o co2_{npruns*i+2} -p '' & "
        + f"pyopmnearwell -i co2_{npruns*i+3}.txt -o co2_{npruns*i+3} -p '' & "
        + f"pyopmnearwell -i co2_{npruns*i+4}.txt -o co2_{npruns*i+4} -p '' & wait"
    )
    for j in range(npruns):
        xcord = np.load(f"./co2_{npruns*i+j}/output/xspace.npy")
        x_centers = 0.5 * (xcord[1:] + xcord[:-1])
        nx_cells = len(x_centers)
        zcord = np.load(f"./co2_{npruns*i+j}/output/zspace.npy")
        z_centers = 0.5 * (zcord[1:] + zcord[:-1])
        nz_cells = len(z_centers)
        smspec = Summary(f"./co2_{npruns*i+j}/output/CO2_{npruns*i+j}.SMSPEC")
        unrst = ResdataFile(f"./co2_{npruns*i+j}/output/CO2_{npruns*i+j}.UNRST")
        init = ResdataFile(f"./co2_{npruns*i+j}/output/CO2_{npruns*i+j}.INIT")
        grid = Grid(f"./co2_{npruns*i+j}/output/CO2_{npruns*i+j}.EGRID")
        phiv = np.array(init.iget_kw("PORV")[0][:])
        sgas = np.array(unrst.iget_kw("SGAS")[-1][:])
        r_s = np.array(unrst.iget_kw("RSW")[-1][:])
        rhog = np.array(unrst.iget_kw("GAS_DEN")[-1][:])
        mass_co2_gas.append(sum(sgas * rhog * phiv))
        mass_co2_dissolved.append(sum(REF_CO2_DENSITY * r_s * (1.0 - sgas) * phiv))
        mass_co2_total.append(mass_co2_gas[-1] + mass_co2_dissolved[-1])
        ratio_co2_dissolved_total.append(mass_co2_dissolved[-1] / mass_co2_total[-1])
        wbhp.append(max(smspec["WBHP:INJ0"].values))
        # Handle the distance part
        indicator_mass = 1.0*((sgas * rhog * phiv) > THRESHOLD_CO2_MASS).reshape(nz_cells, nx_cells)
        max_distance_index = 0
        for row in indicator_mass:
            if max(row) > 0:
                max_distance_index = max(max_distance_index , len(row[::-1]) - pd.Series(row[::-1]).argmax() - 1)
        min_distance_to_boundary.append(xcord[-1] - xcord[1+max_distance_index])
        os.system(f"rm -rf co2_{npruns*i+j} co2_{npruns*i+j}.txt")

np.save('times', times)
np.save('rmdt', ratio_co2_dissolved_total)
np.save('maxwbhp', wbhp)
np.save('mindistance', min_distance_to_boundary)

fig, axis = plt.subplots()
axis.plot(
    times,
    ratio_co2_dissolved_total,
    color="b",
    linestyle="",
    marker="*",
    markersize=5,
)
axis.set_ylabel(r"CO$_2$ ratio of dissolved to total injected [-]", fontsize=12)
axis.set_xlabel(r"Time of one cycle [d]", fontsize=12)
fig.savefig("rmdt.png")

fig, axis = plt.subplots()
axis.plot(
    times,
    wbhp,
    color="b",
    linestyle="",
    marker="*",
    markersize=5,
)
axis.set_ylabel("Maximum Bhp for the injector [Bar]", fontsize=12)
axis.set_xlabel(r"Time of one cycle [d]", fontsize=12)
fig.savefig("maxwbhp.png")

fig, axis = plt.subplots()
axis.plot(
    times,
    min_distance_to_boundary,
    color="b",
    linestyle="",
    marker="*",
    markersize=5,
)
axis.set_ylabel("Minimum distance to boundary [m]", fontsize=12)
axis.set_xlabel(r"Time of one cycle [d]", fontsize=12)
fig.savefig("mindistance.png")
