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
y0 = np.load('ratio_fgpt_to_fgit.npy').reshape(-1, 1)
scale_y0 = MinMaxScaler()
y0_scaled = scale_y0.fit_transform(y0)
y1 = np.load('wbhp.npy').reshape(-1, 1)
scale_y1 = MinMaxScaler()
y1_scaled = scale_y1.fit_transform(y1)
y_scaled = np.stack([y0_scaled.flatten(), y1_scaled.flatten()], axis=-1)

# design the neural network model
model = Sequential(
    [
        tf.keras.Input(shape=(1,)),
        # tf.keras.layers.BatchNormalization(),
        Dense(15, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(15, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(15, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(2),
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

mse = tf.keras.losses.MeanSquaredError()

# Plot w.r.t. x
# plot x vs y
res0 = scale_y0.inverse_transform(
            test0.reshape(-1,1)
        )
res1 = scale_y1.inverse_transform(
            test1.reshape(-1,1)
        )
# plot x vs yhat
pyplot.plot(x_plot, y0, '*', label="Points", markersize=5)
pyplot.plot(
    xv_plot,
    res0,
    label="Predicted",
    linestyle='-',
    linewidth=2,

)
pyplot.xlabel(r"Time of injected H${_2}$ [d]")
pyplot.ylabel(r"Recovered H$_2$ over injected H$_2$ [-]")
pyplot.legend()
pyplot.savefig("ml_ratio_recovered_to_injected.png", dpi=1200)
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
pyplot.xlabel(r"Time of injected H${_2}$ [d]")
pyplot.ylabel("Max bhp [Bar]")
pyplot.legend()
pyplot.savefig("ml_bhp.png", dpi=1200)
pyplot.show()
pyplot.close()
