import csv
import logging
import math

 

import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential
from matplotlib import pyplot
from numpy import asarray
from kerasify import export_model

 

# from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler

logger = logging.getLogger(__name__)

logger.info("Prepare dataset")

# scale h
clip = 2
x_plot = np.load('re.npy')[clip:]
xv_plot = np.linspace(x_plot.min(), x_plot.max(), 30)
scale_x = MinMaxScaler()
scale_xv = MinMaxScaler()
x = scale_x.fit_transform(x_plot.reshape(-1, 1)).squeeze()
xv = scale_xv.fit_transform(xv_plot.reshape(-1, 1)).squeeze()
y = np.load('wi.npy')[clip:].reshape(-1, 1)
scale_y = MinMaxScaler()
y_scaled = scale_y.fit_transform(y)

logger.info("Done")

#pyplot.plot(x, y, '.')
#pyplot.show()

# Write scaling info to file
with open("scales.csv", "w", newline="") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["variable", "min", "max"])
    writer.writeheader()
    writer.writerow(
        {"variable": "h", "min": f"{x_plot.min()}", "max": f"{x_plot.max()}"}
    )
    writer.writerow({"variable": "y", "min": f"{y.min()}", "max": f"{y.max()}"})

# design the neural network model
model = Sequential(
    [
        tf.keras.Input(shape=(1,)),
        # tf.keras.layers.BatchNormalization(),
        Dense(10, activation="tanh", kernel_initializer="glorot_normal"),
        Dense(10, activation="tanh", kernel_initializer="glorot_normal"),
        Dense(10, activation="tanh", kernel_initializer="glorot_normal"),
        Dense(1),
    ]
) 

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor="loss", factor=0.1, patience=10, verbose=1, min_delta=1e-10
)
model.compile(loss="mse", optimizer=tf.keras.optimizers.Adam(learning_rate=0.1))

# ft the model on the training dataset
logger.info("Train model")
model.fit(x, y_scaled, epochs=200, batch_size=10, verbose=1, callbacks=reduce_lr)

# make predictions for the input data
yhat = model.predict(x)
mse = tf.keras.losses.MeanSquaredError()
logger.info(f"MSE: {mse(y, yhat).numpy():.3f}")

# Plot w.r.t. x
# plot x vs y
try:
    # plot x vs yhat
    pyplot.plot(x_plot, y, '*', label="Points", markersize=5)
    pyplot.plot(
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
        linestyle='-',
        linewidth=2,

    )
    pyplot.title("Input (x) versus Output (y)")
    pyplot.xlabel("Time of injection [days]")
    pyplot.ylabel(r"Recovered H${_2}$ [sm${^3}$]")
    pyplot.legend()
    pyplot.savefig("mlkeras.png", dpi=1200)
    pyplot.show()
    pyplot.close()
except Exception as e:
    pass

export_model(model, "water_re.modelPeaceman")