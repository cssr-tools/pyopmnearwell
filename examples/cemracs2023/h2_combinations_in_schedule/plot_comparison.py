import matplotlib.pyplot as plt
import numpy as np
import math as mt

folders=["base_case", "dissolution", "dissolution_wecon", "dissolution_wecon_hyst"]
colors = ["k", "b", "r", "m"]
markers = ["*", "d", "o", "s"]

quantities = ["fgit", "fgpt", "fgit-fgpt"]
descriptions = ["Injected", "Produced", "Injected - Produced"]

for quantity, description in zip(quantities,descriptions): 
    fig, axis = plt.subplots()
    for i, folder in enumerate(folders):
        schedules = np.load(f'{folder}/schedules.npy')
        names = np.load(f'{folder}/names.npy')
        data = np.load(f'{folder}/{quantity}.npy')
        axis.plot(
            range(len(schedules)),
            data,
            color=colors[i],
            linestyle="",
            marker=markers[i],
            markersize=5,
            label=folder,
        )
    if len(schedules) <= 16:
        axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, len(schedules)), 2))
        axis.set_xticklabels(names, rotation=90)
    else:
        axis.set_xticks(np.round(np.linspace(0, len(schedules)-1, 4), 2))
        axis.set_xticklabels([names[0],names[mt.floor(len(schedules)/4)],names[mt.floor(3*len(schedules)/4)],names[-1]], rotation=90)
    axis.set_ylabel(f"{description}" + r" H$_2$ [sm${^3}$]", fontsize=12)
    axis.set_xlabel(r"Sequence in the schedule [-]", fontsize=12)
    axis.legend(fontsize=8)
    fig.savefig(f"{quantity}.png",bbox_inches='tight')