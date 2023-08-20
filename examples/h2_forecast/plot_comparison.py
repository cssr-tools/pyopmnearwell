import matplotlib.pyplot as plt
import numpy as np

folders=["base_case", "dissolution", "dissolution_wecon", "dissolution_wecon_hyst"]
colors = ["k", "b", "r", "m"]
markers = ["*", "d", "o", "s"]

quantities = ["fgit", "fgpt", "fgit-fgpt"]
descriptions = ["Injected", "Produced", "Injected - Produced"]

for quantity, description in zip(quantities,descriptions): 
    fig, axis = plt.subplots()
    for i, folder in enumerate(folders):
        times = np.load(f'{folder}/times.npy')
        data = np.load(f'{folder}/{quantity}.npy')
        axis.plot(
            times,
            data,
            color=colors[i],
            linestyle="",
            marker=markers[i],
            markersize=5,
            label=folder,
        )
    axis.set_ylabel(f"{description}" + r" H$_2$ [sm${^3}$]", fontsize=12)
    axis.set_xlabel("Time (after the 365 d inj + 90 d stop) to assess the operation [d]", fontsize=10)
    axis.legend(fontsize=8, loc='upper left')
    fig.savefig(f"{quantity}.png",bbox_inches='tight')