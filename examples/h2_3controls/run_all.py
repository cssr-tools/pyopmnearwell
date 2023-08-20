import matplotlib.pyplot as plt
import numpy as np
import math as mt
import os
import subprocess
import matplotlib

FLOW = "/Users/dmar/Github/opm/build/opm-simulators/bin/flow"
QRATE = 400000. / 6 # Injection/production rate (as in the comparison paper, divided by 6 since the angle in the cake is 60 degrees)
TPERIOD = 7 # Duration of one period in days
NSCHED = 3  # Number of changues in the schedule
NPRUNS = 4 # Number of parallel simulations

folders = sorted([name for name in os.listdir(".") if os.path.isdir(name)])
cwd = os.getcwd()
for folder in folders:
    os.chdir(f"{cwd}/{folder}")
    subprocess.run(
        ["python3", "run_simulations.py", "-f", f"{FLOW}", "-q", f"{QRATE}", "-t", f"{TPERIOD}", "-n", f"{NSCHED}", "-p", f"{NPRUNS}"], check=True
    )
os.chdir(f"{cwd}")
colors = matplotlib.colormaps["tab20"]
markers = ['o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_', 'P', 'X']

quantities = ["fgit", "fgpt", "fgit-fgpt", "1-fgpt_fgit"]
units = ["sm${^3}$", "sm${^3}$", "sm${^3}$", "-"]
descriptions = ["Injected", "Produced", "Injected - Produced", "(Injected - Produced) / Injected"]

for j,(quantity, description) in enumerate(zip(quantities,descriptions)): 
    fig, axis = plt.subplots()
    for i, folder in enumerate(folders):
        schedules = np.load(f'{folder}/schedules.npy')
        names = np.load(f'{folder}/names.npy')
        data = np.load(f'{folder}/{quantity}.npy')
        axis.plot(
            range(len(schedules)),
            data,
            color=colors(i),
            linestyle="",
            marker=markers[i],
            markersize=5,
            label=folder,
        )
    if len(schedules) <= 27:
        axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, len(schedules)), 2))
        axis.set_xticklabels(names, rotation=90)
    else:
        axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, 4), 2))
        axis.set_xticklabels([names[0],names[mt.floor(len(schedules)/4)],names[mt.floor(3*len(schedules)/4)],names[-1]], rotation=90)
    ylabel = description + " H$_2$ " + f"[{units[j]}]"
    axis.set_ylabel(f"{ylabel}", fontsize=12)
    axis.set_xlabel(r"Sequence in the schedule [-]", fontsize=12)
    axis.legend(fontsize=6, loc='upper left')
    fig.savefig(f"{quantity}.png",bbox_inches='tight')