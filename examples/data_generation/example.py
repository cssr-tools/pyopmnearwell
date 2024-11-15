# SPDX-FileCopyrightText: 2024 NORCE
# SPDX-License-Identifier: GPL-3.0

""""
Script to run Flow for a random input variable; gas injection rate in this case.
The gas injection times are scaled to have the same injected volumes
"""

import os
import math as mt
import numpy as np
import warnings
from mako.template import Template
import matplotlib.pyplot as plt
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from resdata.summary import Summary

np.random.seed(7)

EOR = "foam" # Select foam or co2eor
GRATES = np.random.uniform(10, 3000, 110) # Randomly sampled gas injection rate values
NSCHED = 25 # Number of cycles (one period is water injection followd by gas injection)
WTIME = 90 # Duration of the water injection period in days
WRATE = 45000 # Water injection rate
GVOL = 270000 # Target gas volume to inject in a period (i.e., larger grates would have shorter injection periods so all grates cases inject the same volumes)
NPRUNS = 11 # Number of paralell runs (it should be limited by the number of your cpus)
DELETE = 1 # Set to 0 to no delete the simulation files (careful with your PC memmory)
FLOW = "/Users/dmar/Github/opm/build/opm-simulators/bin/flow" # Set the path to the flow executable

# Initialize the variables to read and plot (if new variables are added, in lines 54-59 you can read the vectors from the summary file)
names = {'ratio_oil_to_inj_vol': []}
for name in ['oil_pro_vol','wat_inj_vol','wat_pro_vol','gas_inj_vol','gas_pro_vol']:
    names[name] = []

# Generate the confi files, run the simulations, read the data, and delete if requiered
mytemplate = Template(filename="eor.mako") 
for i, grate in enumerate(GRATES):
    var = {"flow": FLOW, "grate": grate, "eor": EOR, "wtime":WTIME, "wrate":WRATE, "gvol":GVOL, "nsched":NSCHED}
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{EOR}_{i}.txt",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)

for i in range(mt.floor(len(GRATES) / NPRUNS)):
    command = ""
    for j in range(NPRUNS):
        if DELETE == 1:
            command += f"pyopmnearwell -i {EOR}_{NPRUNS*i+j}.txt -o {EOR}_{NPRUNS*i+j} -g single -w no & "
        else:
            command += f"pyopmnearwell -i {EOR}_{NPRUNS*i+j}.txt -o {EOR}_{NPRUNS*i+j} -g single & "
    command += "wait"
    os.system(command)
    for j in range(NPRUNS):
        smspec = Summary(f"./{EOR}_{NPRUNS*i+j}/{EOR}_{NPRUNS*i+j}.SMSPEC")
        names["wat_inj_vol"].append(smspec["FWIT"].values[-1])
        names["wat_pro_vol"].append(smspec["FWPT"].values[-1])
        names["gas_inj_vol"].append(smspec["FGIT"].values[-1])
        names["gas_pro_vol"].append(smspec["FGPT"].values[-1])
        names["oil_pro_vol"].append(smspec["FOPT"].values[-1])
        names["ratio_oil_to_inj_vol"].append(smspec["FOPT"].values[-1]/(smspec["FGIT"].values[-1]+smspec["FWIT"].values[-1]))
        if DELETE == 1:
            os.system(f"rm -rf {EOR}_{NPRUNS*i+j} {EOR}_{NPRUNS*i+j}.txt")
finished = NPRUNS * mt.floor(len(GRATES) / NPRUNS)
remaining = len(GRATES) - finished
command = ""
for i in range(remaining):
    if DELETE == 1:
        command += f"pyopmnearwell -i {EOR}_{finished+i}.txt -o {EOR}_{finished+i} -g single -w no & "
    else:
        command += f"pyopmnearwell -i {EOR}_{finished+i}.txt -o {EOR}_{finished+i} -g single & "
command += "wait"
os.system(command)
for i in range(remaining):
    smspec = Summary(f"./{EOR}_{finished+i}/{EOR}_{finished+i}.SMSPEC")
    ratio_oil_to_injected_volumes.append(smspec["FOPT"].values[-1]/(smspec["FGIT"].values[-1]+smspec["FWIT"].values[-1]))
    if DELETE == 1:
        os.system(f"rm -rf {EOR}_{finished+i} {EOR}_{finished+i}.txt")

# Save variables to numpy objects
np.save('grates', GRATES)
for key in names.keys():
    np.save(EOR+"_"+key, names[key])

# Plot the variables for quick inspection
for name in names.keys():
    fig, axis = plt.subplots()
    axis.plot(
        GRATES,
        names[name],
        color="b",
        linestyle="",
        marker="*",
        markersize=5,
    )
    axis.set_ylabel(name, fontsize=12)
    axis.set_xlabel(r"Gas injection rate [stb/day]", fontsize=12)
    fig.savefig(f"{EOR}_{name}.png")