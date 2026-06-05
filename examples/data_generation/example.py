# SPDX-FileCopyrightText: 2024-2026, NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R1732,C0301

""" "Script to run Flow for a random input variable; gas injection rate in this case.
The gas injection times are scaled to have the same injected volumes"""

import subprocess
import warnings
import math as mt
import numpy as np
from mako.template import Template
import matplotlib.pyplot as plt

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    from resdata.summary import Summary

np.random.seed(7)

EOR = "foam"  # Select foam or co2eor
GRATES = np.random.uniform(10, 3000, 11)  # Randomly sampled gas injection rate values
NSCHED = 25  # Number of cycles (one period is water injection followed by gas injection)
WTIME = 90  # Duration of the water injection period in days
WRATE = 45000  # Water injection rate
GVOL = 270000  # Target gas volume to inject in a period (i.e., larger grates would have shorter injection periods so all grates cases inject the same volumes)
NPRUNS = 5  # Number of paralell runs (it should be limited by the number of your cpus)
DELETE = 1  # Set to 0 to no delete the simulation files (careful with your PC memmory)
FLOW = "flow"  # Set the path to the flow executable

# Initialize the variables to read and plot (if new variables are added, in lines 54-59 you can read the vectors from the summary file)
names = {"ratio_oil_to_inj_vol": []}
for name in ["oil_pro_vol", "wat_inj_vol", "wat_pro_vol", "gas_inj_vol", "gas_pro_vol"]:
    names[name] = []


def run_cases(start_index, count):
    "Run pyopmnearwell"
    processes = []
    for index in range(count):
        case_id = start_index + index
        if DELETE == 1:
            processes.append(
                subprocess.Popen(
                    [
                        "pyopmnearwell",
                        "-i",
                        f"{EOR}_{case_id}.toml",
                        "-o",
                        f"{EOR}_{case_id}",
                        "-m",
                        "single",
                        "-v",
                        "0",
                    ]
                )
            )
        else:
            processes.append(
                subprocess.Popen(
                    [
                        "pyopmnearwell",
                        "-i",
                        f"{EOR}_{case_id}.toml",
                        "-o",
                        f"{EOR}_{case_id}",
                        "-m",
                        "single",
                    ]
                )
            )
    for process in processes:
        process.wait()
    for index in range(count):
        case_id = start_index + index
        smspec = Summary(f"./{EOR}_{case_id}/{EOR.upper()}_{case_id}.SMSPEC")
        names["wat_inj_vol"].append(smspec["FWIT"].values[-1])
        names["wat_pro_vol"].append(smspec["FWPT"].values[-1])
        names["gas_inj_vol"].append(smspec["FGIT"].values[-1])
        names["gas_pro_vol"].append(smspec["FGPT"].values[-1])
        names["oil_pro_vol"].append(smspec["FOPT"].values[-1])
        names["ratio_oil_to_inj_vol"].append(
            smspec["FOPT"].values[-1]
            / (smspec["FGIT"].values[-1] + smspec["FWIT"].values[-1])
        )
        if DELETE == 1:
            subprocess.run(
                ["rm", "-rf", f"{EOR}_{case_id}", f"{EOR.upper()}_{case_id}.toml"],
                check=True
            )


# Generate the confi files, run the simulations, read the data, and delete if requiered
mytemplate = Template(filename="eor.mako")
for i, grate in enumerate(GRATES):
    var = {
        "flow": FLOW,
        "grate": grate,
        "eor": EOR,
        "wtime": WTIME,
        "wrate": WRATE,
        "gvol": GVOL,
        "nsched": NSCHED,
    }
    filledtemplate = mytemplate.render(**var)
    with open(
        f"{EOR}_{i}.toml",
        "w",
        encoding="utf8",
    ) as file:
        file.write(filledtemplate)

for i in range(mt.floor(len(GRATES) / NPRUNS)):
    run_cases(NPRUNS * i, NPRUNS)

finished = NPRUNS * mt.floor(len(GRATES) / NPRUNS)
remaining = len(GRATES) - finished
if remaining > 0:
    run_cases(finished, remaining)

# Save variables to numpy objects
np.save("grates", GRATES)
for key, value in names.items():
    np.save(EOR + "_" + key, value)

# Plot the variables for quick inspection
for _, value in names.items():
    fig, axis = plt.subplots()
    axis.plot(
        GRATES,
        value,
        color="b",
        linestyle="",
        marker="*",
        markersize=5,
    )
    axis.set_ylabel(name, fontsize=12)
    axis.set_xlabel(r"Gas injection rate [stb/day]", fontsize=12)
    fig.savefig(f"{EOR}_{name}.png")
