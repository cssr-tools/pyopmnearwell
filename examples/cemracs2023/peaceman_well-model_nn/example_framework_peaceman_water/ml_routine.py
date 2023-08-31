# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-FileCopyrightText: 2023 UiB
# SPDX-License-Identifier: GPL-3.0

""""
Script to run the ML routine
"""

import os
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from keras.layers import Dense
from keras.models import Sequential
from kerasify import export_model
from sklearn.preprocessing import MinMaxScaler
from mako.template import Template
from pyopmnearwell.ml.kerasify import export_model

tf.keras.utils.set_random_seed(42)

# Give the path to the OPM Flow ML repos
PYOPM = "/Users/dmar/Github/pyopmnearwell/examples/cemracs2023/peaceman_well-model_nn"

# Load the variables
r_input = np.load("re.npy")
rw_input = np.load("rw.npy")
k_input = np.load("kh.npy")
wi = np.load("wi.npy")

# Scale r
r_validation = np.linspace(r_input.min(), r_input.max(), len(r_input) + 1)
scale_r = MinMaxScaler()
scale_rv = MinMaxScaler()
r = scale_r.fit_transform(r_input.reshape(-1, 1)).squeeze()
r_validation_scaled = scale_rv.fit_transform(r_validation.reshape(-1, 1)).squeeze()

# Scale rw
rw_validation = np.linspace(rw_input.min(), rw_input.max(), len(rw_input) + 1)
scale_rw = MinMaxScaler()
scale_rwv = MinMaxScaler()
rw = scale_rw.fit_transform(rw_input.reshape(-1, 1)).squeeze()
rw_validation_scaled = scale_rwv.fit_transform(rw_validation.reshape(-1, 1)).squeeze()

# Scale k
k_validation = np.linspace(k_input.min(), k_input.max(), len(k_input))
scale_k = MinMaxScaler()
scale_kv = MinMaxScaler()
k = scale_k.fit_transform(k_input.reshape(-1, 1)).squeeze()
k_validation_scaled = scale_kv.fit_transform(k_validation.reshape(-1, 1)).squeeze()

# Mesh
rw_m, k_m, r_m = np.meshgrid(rw, k, r)
rw_input_mesh, k_input_mesh, r_input_mesh = np.meshgrid(rw_input, k_input, r_input)
rw_validation_mesh, k_validation_mesh, r_validation_mesh = np.meshgrid(rw_validation, k_validation, r_validation)
rw_mv, k_mv, r_mv = np.meshgrid(rw_validation_scaled, k_validation_scaled, r_validation_scaled)

# Together
x = np.stack([rw_m.flatten(), k_m.flatten(), r_m.flatten()], axis=-1)
x_ref = np.stack([rw_mv.flatten(), k_mv.flatten(), r_mv.flatten()], axis=-1)
x_input = np.stack([rw_input_mesh.flatten(), k_input_mesh.flatten(), r_input_mesh.flatten()], axis=-1)
k_inx = pd.Series(k_input-k_input.min()).argmin()
rw_inx = pd.Series(rw_input-rw_input.min()).argmin()
wi_r_ref = wi[0][:len(r_input)+1]
wi_k_ref = [row[0] for row in wi[:len(k_input)]]
y_ref = wi
y = y_ref.reshape(-1, 1)
scale_y = MinMaxScaler()
y_scaled = scale_y.fit_transform(y)

# ML
model = Sequential(
    [
        tf.keras.Input(shape=(3,)),
        Dense(10, activation="sigmoid"),
        Dense(10, activation="sigmoid"),
        Dense(10, activation="sigmoid"),
        Dense(10, activation="sigmoid"),
        Dense(10, activation="sigmoid"),
        Dense(1),
    ]
)
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor="loss", factor=0.12, patience=10, verbose=1, min_delta=1e-10
)
model.compile(loss="mse", optimizer=tf.keras.optimizers.Nadam(learning_rate=0.12))
model.fit(x, y_scaled, epochs=200, batch_size=100, verbose=1, callbacks=reduce_lr)
export_model(model, "water_re.modelPeaceman")

# Make figures
plt.plot(r_input, wi_r_ref, "*", label="Data", markersize=5)
plt.plot(
    r_validation,
    scale_y.inverse_transform(
        model(
            np.stack(
                [
                    np.full_like(r_validation_scaled, rw_validation_scaled[0]),
                    np.full_like(r_validation_scaled, k_validation_scaled[0]),
                    r_validation_scaled,
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
plt.ylabel(r"WI [sm${^3}$/(Pa s)]")
plt.legend()
plt.savefig("mlkerasdistance.png", dpi=1200)
plt.close()

plt.plot(k_input, wi_k_ref, "*", label="Data", markersize=5)
plt.plot(
    k_validation,
    scale_y.inverse_transform(
        model(
            np.stack(
                [
                    np.full_like(k_validation_scaled, rw_validation_scaled[0]),
                    k_validation_scaled,
                    np.full_like(k_validation_scaled, r_validation_scaled[0]),
                ],
                axis=-1,
            )
        )
    ),
    label="Predicted",
    linestyle="-",
    linewidth=2,
)

plt.xlabel("Permeability [mD]")
plt.ylabel(r"WI [sm${^3}$/(Pa s)]")
plt.legend()
plt.savefig("mlkeraspermeability.png", dpi=1200)
plt.close()

# fig = plt.figure()
# ax = plt.axes(projection="3d")
# ax.plot_surface(
#     r_validation_mesh,
#     k_validation_mesh,
#     scale_y.inverse_transform(model(x_ref)).reshape(len(k_validation), len(r_validation)),
#     rstride=1,
#     cstride=1,
#     cmap="viridis",
#     edgecolor="none",
# )
# fig.savefig("mlkeras_surface.png", dpi=1200)
# plt.close()

# fig = plt.figure()
# ax = plt.axes(projection="3d")
# ax.plot_surface(
#     r_input_mesh, k_input_mesh, y_ref, rstride=1, cstride=1, cmap="viridis", edgecolor="none"
# )
# fig.savefig("data_surface.png", dpi=1200)
# plt.close()

# Write scaling info to opm and recompile (quick fix before the scaling layers work)
xmin = [rw_input.min(), k_input.min(), r_input.min()]
xmax = [rw_input.max(), k_input.max(), r_input.max()]
ymin = y.min()
ymax = y.max()
var = {"xmin": xmin, "xmax": xmax, "ymin": ymin, "ymax": ymax}
mytemplate = Template(filename="StandardWell_impl.mako")
filledtemplate = mytemplate.render(**var)
with open(
    f"{PYOPM}/opm-simulators/opm/simulators/wells/StandardWell_impl.hpp",
    "w",
    encoding="utf8",
) as file:
    file.write(filledtemplate)
pwd = os.getcwd()
os.chdir(f"{PYOPM}/build/opm-simulators")
os.system("make -j5 flow_gaswater_dissolution_diffuse")
os.chdir(f"{pwd}")