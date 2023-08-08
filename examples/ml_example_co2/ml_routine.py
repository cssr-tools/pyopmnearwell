import numpy as np
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential
from matplotlib import pyplot

# from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler

tf.keras.utils.set_random_seed(42)

# scale h
xv_plot = np.linspace(0, 365, 30)
x_plot = np.load('times.npy')
scale_x = MinMaxScaler()
scale_xv = MinMaxScaler()
x = scale_x.fit_transform(x_plot.reshape(-1, 1)).squeeze()
xv = scale_xv.fit_transform(xv_plot.reshape(-1, 1)).squeeze()
y0 = np.load('rmdt.npy').reshape(-1, 1)
scale_y0 = MinMaxScaler()
y0_scaled = scale_y0.fit_transform(y0)
y1 = np.load('maxwbhp.npy').reshape(-1, 1)
scale_y1 = MinMaxScaler()
y1_scaled = scale_y1.fit_transform(y1)
y2 = np.load('mindistance.npy').reshape(-1, 1)
scale_y2 = MinMaxScaler()
y2_scaled = scale_y2.fit_transform(y2)
y_scaled = np.stack([y0_scaled.flatten(), y1_scaled.flatten(), y2_scaled.flatten()], axis=-1)

# design the neural network model
model = Sequential(
    [
        tf.keras.Input(shape=(1,)),
        # tf.keras.layers.BatchNormalization(),
        Dense(15, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(15, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(15, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(3),
    ]
) 

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor="loss", factor=0.1, patience=10, verbose=1, min_delta=1e-10
)
model.compile(loss="mse", optimizer=tf.keras.optimizers.Adam(learning_rate=0.1))
model.fit(x, y_scaled, epochs=1000, batch_size=10, verbose=1, callbacks=reduce_lr)

test0 = np.array([row[0] for row in model(
                np.stack(
                    [
                        xv,
                    ],
                    axis=-1,
                )
            )])
test1 = np.array([row[1] for row in model(
                np.stack(
                    [
                        xv,
                    ],
                    axis=-1,
                )
            )])
test2 = np.array([row[2] for row in model(
                np.stack(
                    [
                        xv,
                    ],
                    axis=-1,
                )
            )])

mse = tf.keras.losses.MeanSquaredError()

# Plot w.r.t. x
# plot x vs y
res0 = scale_y0.inverse_transform(
            test0.reshape(-1,1)
        )
res1 = scale_y1.inverse_transform(
            test1.reshape(-1,1)
        )
res2 = scale_y2.inverse_transform(
            test2.reshape(-1,1)
        )
# plot x vs ys
pyplot.plot(x_plot, y0, '*', label="Points", markersize=5)
pyplot.plot(
    xv_plot,
    res0,
    label="Predicted",
    linestyle='-',
    linewidth=2,

)
pyplot.xlabel(r"Time of one cycle [d]")
pyplot.ylabel(r"CO$_2$ ratio of dissolved to total injected [-]")
pyplot.legend()
pyplot.savefig("ml_rmdt.png", dpi=1200)
pyplot.show()
pyplot.close()

pyplot.plot(x_plot, y1, '*', label="Points", markersize=5)
pyplot.plot(
    xv_plot,
    res1,
    label="Predicted",
    linestyle='-',
    linewidth=2,

)
pyplot.xlabel(r"Time of one cycle [d]")
pyplot.ylabel("Maximum Bhp for the injector [Bar]")
pyplot.legend()
pyplot.savefig("ml_maxwbhp.png", dpi=1200)
pyplot.show()
pyplot.close()

pyplot.plot(x_plot, y2, '*', label="Points", markersize=5)
pyplot.plot(
    xv_plot,
    res2,
    label="Predicted",
    linestyle='-',
    linewidth=2,

)
pyplot.xlabel(r"Time of one cycle [d]")
pyplot.ylabel("Minimum distance to boundary [m]")
pyplot.legend()
pyplot.savefig("ml_mindistance.png", dpi=1200)
pyplot.show()
pyplot.close()
