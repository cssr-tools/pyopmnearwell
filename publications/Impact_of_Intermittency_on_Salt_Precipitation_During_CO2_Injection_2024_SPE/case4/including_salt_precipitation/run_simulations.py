# SPDX-FileCopyrightText: 2024-2026 NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1732,R0914,W0603,W0621,C0103,W0602

"""Script to run Flow"""

import subprocess
from pathlib import Path
import math as mt
import itertools
import datetime
import numpy as np
from opm.io.ecl import ERst as OpmRestart
from opm.io.ecl import ESmry as OpmSummary
from opm.io.ecl import EGrid as OpmGrid
from mako.template import Template
import matplotlib.pyplot as plt

whr = Path(__file__).resolve().parent

FLOW = "flow"
TPERIOD = 365
NSCHED = 3
NPRUNS = 16
REF_CO2_DENSITY = 1.86843
WAT_DEN_REF = 998.108
THRESHOLD_CO2_MASS = 100

scheduless = list(itertools.product("01", repeat=2**NSCHED))
seq_string = ["".join(seq) for seq in itertools.product("01", repeat=2**NSCHED)]
for index, row in enumerate(scheduless):
    scheduless[index] = [int(column) for column in row]
ordered = np.argsort(np.array([np.sum(row) for row in scheduless]))
scheduless = np.array(scheduless)[ordered]
namess = []
for index in ordered:
    namess.append(seq_string[index])
schedules = []
names = []
for index, row in enumerate(scheduless):
    if np.sum(row) == 2 ** (NSCHED - 1) and row[0] > 0:
        schedules.append(row)
        names.append(namess[index])
del schedules[10]
schedules.insert(0, [1, 0, 1, 0, 1, 0, 1, 0])
del schedules[28]
schedules.insert(len(schedules), [1, 1, 1, 1, 0, 0, 0, 0])
nsimulations = len(schedules)
names.remove("10101010")
names.remove("11110000")
names.insert(0, "10101010")
names.insert(len(names), "11110000")

mytemplate = Template(filename=f"{whr}/co2.mako")

grid_loaded = False
xcord_global = None

fgmit = []
mass_salt = []
ratio_co2_dissolved_total = []
min_distance_to_boundary = []
wbhp, wbhpxyear = [], []


def load_grid_once(case_index):
    """Load the grid"""
    global grid_loaded, xcord_global
    if not grid_loaded:
        grid = OpmGrid(f"{whr}/co2_{case_index}/output/CO2_{case_index}.EGRID")
        nx = grid.dimension[0]
        xcord_global = np.zeros(nx, dtype=np.float32)
        for i in range(nx):
            coord = grid.xyz_from_ijk(i, 0, 0)
            xcord_global[i] = np.array(coord).flatten()[0]
        grid_loaded = True


def process_case(case_index):
    """Process the case"""
    global xcord_global
    load_grid_once(case_index)
    smspec = OpmSummary(f"{whr}/co2_{case_index}/output/CO2_{case_index}.SMSPEC")
    restart = OpmRestart(f"{whr}/co2_{case_index}/output/CO2_{case_index}.UNRST")
    report_step = len(restart) - 1
    time = []
    for index_time in range(len(restart)):
        intehead = restart["INTEHEAD", index_time]
        time.append(datetime.datetime(intehead[66], intehead[65], intehead[64], 0, 0))
    times = np.diff(np.array(time)) / np.timedelta64(1, "s")
    intehead0 = restart["INTEHEAD", 0]
    nx = int(intehead0[8])
    ny = int(intehead0[9])
    nz = int(intehead0[10])
    saltp = np.array(restart["SALTP", report_step], dtype=np.float32)
    phiv = np.array(restart["RPORV", report_step], dtype=np.float32)
    sgas = np.array(restart["SGAS", report_step], dtype=np.float32)
    rhog = np.array(restart["GAS_DEN", report_step], dtype=np.float32)
    xcord = xcord_global
    mass_salt.append(np.sum(saltp * phiv) * 2153 / 1000.0)
    ratio_co2_dissolved_total.append(100 * smspec["FGMDS"][-1] / smspec["FGMIP"][-1])
    wellp = smspec["WBHP:INJ0"]
    wbhp.append(np.max(wellp))
    wbhpxyear.append(np.sum(times * (0.5 * (wellp[1:] + wellp[:-1]))) / (86400.0 * 365))
    indicator_mass = (
        ((sgas * rhog * phiv) > THRESHOLD_CO2_MASS)
        .astype(np.float32)
        .reshape(nz * ny, nx)
    )
    max_distance_index = 0
    for row in indicator_mass:
        if np.max(row) > 0:
            reversed_row = row[::-1]
            arg_index = np.argmax(reversed_row > 0)
            max_distance_index = max(max_distance_index, len(row) - arg_index - 1)
    min_distance_to_boundary.append(xcord[max_distance_index])
    fgmit.append(smspec["FGMIT"][-1])
    del saltp, phiv, sgas, rhog, indicator_mass
    subprocess.run(
        f"rm -rf {whr}/co2_{case_index} {whr}/co2_{case_index}.toml",
        shell=True,
        check=True,
    )


for index, schedule in enumerate(schedules):
    var = {"flow": FLOW, "tperiod": TPERIOD, "schedule": schedule}
    filledtemplate = mytemplate.render(**var)
    with open(f"{whr}/co2_{index}.toml", "w", encoding="utf8") as file:
        file.write(filledtemplate)

for batch_index in range(mt.floor(nsimulations / NPRUNS)):
    processes = []
    for run_index in range(NPRUNS):
        case_index = NPRUNS * batch_index + run_index
        processes.append(
            subprocess.Popen(
                [
                    "pyopmnearwell",
                    "-i",
                    f"{whr}/co2_{case_index}.toml",
                    "-o",
                    f"{whr}/co2_{case_index}",
                ]
            )
        )
    for process in processes:
        process.wait()
    for run_index in range(NPRUNS):
        process_case(NPRUNS * batch_index + run_index)

finished = NPRUNS * mt.floor(nsimulations / NPRUNS)
remaining = nsimulations - finished
processes = []
for index in range(remaining):
    case_index = finished + index
    processes.append(
        subprocess.Popen(
            [
                "pyopmnearwell",
                "-i",
                f"{whr}/co2_{case_index}.toml",
                "-o",
                f"{whr}/co2_{case_index}",
            ]
        )
    )
for process in processes:
    process.wait()
for run_index in range(remaining):
    process_case(finished + run_index)

np.save(f"{whr}/fgmit", np.array(fgmit, dtype=np.float32))
np.save(f"{whr}/rmdt", np.array(ratio_co2_dissolved_total, dtype=np.float32))
np.save(f"{whr}/maxwbhp", np.array(wbhp, dtype=np.float32))
np.save(f"{whr}/bhpxyear", np.array(wbhpxyear, dtype=np.float32))
np.save(f"{whr}/mindistance", np.array(min_distance_to_boundary, dtype=np.float32))
np.save(f"{whr}/names", names)
np.save(f"{whr}/mass_salt", np.array(mass_salt, dtype=np.float32))
np.save(f"{whr}/schedules", schedules)

quantities = ["fgmit", "rmdt", "maxwbhp", "mindistance", "bhpxyear", "mass_salt"]
units = ["sm$^3$", "-", "bar", "m", "bar year", "t"]
descriptions = [
    "Injected CO2",
    "Ratio of dissolved CO2 to total",
    "Max well BHP",
    "CO2 distance to the well",
    "Well BHP integretaed over time",
    "Precipitated salt",
]

for j, (quantity, description) in enumerate(zip(quantities, descriptions)):
    fig, axis = plt.subplots()
    data = np.load(f"{whr}/{quantity}.npy")
    axis.plot(
        range(len(schedules)), data, color="k", linestyle="", marker="*", markersize=5
    )
    if len(schedules) <= 38:
        axis.set_xticks(np.round(np.linspace(0, len(schedules) - 1, len(schedules)), 2))
        axis.set_xticklabels(names, rotation=270)
    else:
        axis.set_xticks(np.round(np.linspace(0, len(schedules) - 1, 4), 2))
        axis.set_xticklabels(
            [
                names[0][0:6] + "...",
                names[mt.floor(len(schedules) / 4)],
                names[mt.floor(3 * len(schedules) / 4)][0:6] + "...",
                names[-1][0:6] + "...",
            ],
            rotation=270,
        )
    ylabel = description + f" [{units[j]}]"
    axis.set_ylabel(f"{ylabel}", fontsize=12)
    if quantity in ["fgmit", "rmdt", "mindistance"]:
        axis.set_ylim(0)
    axis.set_xlabel(r"Sequence in the schedule [-]", fontsize=12)
    fig.savefig(f"{whr}/{quantity}.png", bbox_inches="tight")
