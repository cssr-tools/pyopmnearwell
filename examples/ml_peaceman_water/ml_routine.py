# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-FileCopyrightText: 2023 UiB
# SPDX-License-Identifier: GPL-3.0

""""
Script to run the ML routine
"""

import csv
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from keras.layers import Dense
from keras.models import Sequential
from kerasify import export_model
from sklearn.preprocessing import MinMaxScaler

tf.keras.utils.set_random_seed(42)

# Scale the input and output data
SKIPED_VALUES = 20
x_plot = np.load("re.npy")[SKIPED_VALUES:]
xv_plot = np.linspace(x_plot.min(), x_plot.max(), 30)
scale_x = MinMaxScaler()
scale_xv = MinMaxScaler()
x = scale_x.fit_transform(x_plot.reshape(-1, 1)).squeeze()
xv = scale_xv.fit_transform(xv_plot.reshape(-1, 1)).squeeze()
y = np.load("wi.npy")[SKIPED_VALUES:].reshape(-1, 1)
scale_y = MinMaxScaler()
y_scaled = scale_y.fit_transform(y)

# Write scaling info to file
with open("scales.csv", "w", newline="", encoding="utf8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["variable", "min", "max"])
    writer.writeheader()
    writer.writerow(
        {"variable": "h", "min": f"{x_plot.min()}", "max": f"{x_plot.max()}"}
    )
    writer.writerow({"variable": "y", "min": f"{y.min()}", "max": f"{y.max()}"})

# ML routine
model = Sequential(
    [
        tf.keras.Input(shape=(1,)),
        Dense(20, activation="sigmoid"),
        Dense(20, activation="sigmoid"),
        Dense(20, activation="sigmoid"),
        Dense(1),
    ]
)
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor="loss", factor=0.12, patience=10, verbose=1, min_delta=1e-10
)
model.compile(loss="mse", optimizer=tf.keras.optimizers.Nadam(learning_rate=0.12))
model.fit(x, y_scaled, epochs=200, batch_size=10, verbose=1, callbacks=reduce_lr)
export_model(model, "water_re.modelPeaceman")

# Plot the results
plt.plot(x_plot, y, "*", label="Data", markersize=5)
plt.plot(
    xv_plot,
    scale_y.inverse_transform(
        model(
            np.stack(
                [
                    xv,
                ],
                axis=-1,
            )
        )
    ),
    label="Predicted",
    linestyle="-",
    linewidth=2,
)
plt.xlabel("Distance to well [m]")
plt.ylabel(r"WI [sm{^3}/(Pa s)]")
plt.legend()
plt.savefig("ml_wellindex_comparison.png", dpi=1200)
plt.close()
