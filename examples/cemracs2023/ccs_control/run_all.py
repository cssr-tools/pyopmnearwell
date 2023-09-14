import matplotlib.pyplot as plt
import numpy as np
import math as mt
import os
import subprocess
import matplotlib

FLOW = "/Users/dmar/Github/opm/build/opm-simulators/bin/flow"
TPERIOD = 60 # Duration of one period in days
NSCHED = 3  # Number of changues in the schedule
NPRUNS = 5 # Number of parallel simulations

folders = sorted([name for name in os.listdir(".") if os.path.isdir(name)])
cwd = os.getcwd()
for folder in folders:
   os.chdir(f"{cwd}/{folder}")
   subprocess.run(
       ["python3", "run_simulations.py", "-f", f"{FLOW}", "-t", f"{TPERIOD}", "-n", f"{NSCHED}", "-p", f"{NPRUNS}"], check=True
   )
os.chdir(f"{cwd}")
colors = matplotlib.colormaps["tab20"]
markers = ['o', 'v', '^', '<', '>', 'D', '1', '2', '3', '4', '8', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_', 'P', 'X']

quantities = ["fgit", "rmdt", 'maxwbhp', 'mindistance']
units = ["sm$^3$", "-", "bar", "m"]
descriptions = ["Injected CO2", "Ratio of dissolved CO2 to total", "Max BHP", "Min distance to the reservoir boundary"]

for j,(quantity, description) in enumerate(zip(quantities,descriptions)): 
    fig, axis = plt.subplots()
    for i, folder in enumerate(folders):
        schedules = np.load(f'{folder}/schedules.npy')
        data = np.load(f'{folder}/{quantity}.npy')
        names = np.load(f'{folder}/names.npy')
        axis.plot(
            range(len(schedules)),
            data,
            color=colors(i),
                linestyle="",
                marker=markers[i],
                markersize=5,
                label=folder,
        )
    axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, len(schedules)), 2))
    axis.set_xticklabels(names, rotation=270)
    ylabel = description + f"[{units[j]}]"
    axis.set_ylabel(f"{ylabel}", fontsize=12)
    axis.set_ylim(0)
    axis.set_xlabel(r"Sequence in the schedule [-]", fontsize=12)
    axis.legend(fontsize=8, loc='best')
    fig.savefig(f"{quantity}.png",bbox_inches='tight')