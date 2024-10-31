import matplotlib.pyplot as plt
import numpy as np
import math as mt
import os
import subprocess
import matplotlib

FLOW = "/Users/dmar/Github/opm/build/opm-simulators/bin/flow"
QRATEW = 15000 # Injection rates [stb]
QRATEG = 15000 # Injection rates [Mscf] * 5.6146e-3
TPERIOD = 80 # Duration of one period in days
NSCHED = 8  # Number of changues in the schedule
NPRUNS = 10 # Number of parallel simulations

folders = sorted([name for name in os.listdir(".") if os.path.isdir(name)])
cwd = os.getcwd()
for folder in folders:
   os.chdir(f"{cwd}/{folder}")
   subprocess.run(
       ["python3", "run_simulations.py", "-f", f"{FLOW}", "-q", f"{QRATEW}", "-g", f"{QRATEG}", "-t", f"{TPERIOD}", "-n", f"{NSCHED}", "-p", f"{NPRUNS}"], check=True
   )
os.chdir(f"{cwd}")
colors = matplotlib.colormaps["tab20"]
markers = ['o', 'v', '^', '<', '>', 'D', '1', '2', '3', '4', '8', 's', 'p', '*', 'h', 'H', '+', 'x', 'D', 'd', '|', '_', 'P', 'X']

quantities = ["fvit", "fvpt", "fvit-fvpt", "fnit", "fnpt", "fnit-fnpt", "1-fvpt_fvit", "fopt"]
units = ["stb", "stb", "stb","stb", "stb", "stb", "-", "stb"]
descriptions = ["Injected", "Produced", "Injected - Produced", "Injected CO2", "Produced CO2", "Injected - Produced CO2", "(Injected - Produced) / Injected", "Produced OIL"]

for j,(quantity, description) in enumerate(zip(quantities,descriptions)): 
    fig, axis = plt.subplots()
    for i, folder in enumerate(folders):
        schedules = np.load(f'{folder}/schedules.npy')
        #names = np.load(f'{folder}/names.npy')
        data = np.load(f'{folder}/{quantity}.npy')
        axis.plot(
            range(len(schedules)),
            data,
            color=colors(i),
            linestyle="",
            marker=markers[i],
            markersize=7,
            label=folder,
        )
    #if len(schedules) <= 27:
    #axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, len(schedules)), 2))
    #axis.set_xticklabels([name[0:6]+'...' for name in names], rotation=270)
    axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, len(schedules)), 2))
    axis.set_xticklabels([f'Seq{name}' for name in range(len(schedules))])
    #else:
        #axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, 4), 2))
        #axis.set_xticklabels([names[0],names[mt.floor(len(schedules)/4)][0:6]+'...',names[mt.floor(3*len(schedules)/4)][0:6]+'...',names[-1][0:6]+'...'], rotation=270)
    ylabel = description + f"[{units[j]}]"
    axis.set_ylabel(f"{ylabel}", fontsize=12)
    axis.set_xlabel(r"Sequence in the schedule [-]", fontsize=12)
    axis.legend(fontsize=8, loc='best')
    fig.savefig(f"{quantity}.png",bbox_inches='tight')