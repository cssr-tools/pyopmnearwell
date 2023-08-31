import numpy as np
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential
from matplotlib import pyplot

# from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler

tf.keras.utils.set_random_seed(42)

# scale the x and y data
xv_plot = np.linspace(1000, 3000, 30)
x_plot = np.load('rates.npy')
scale_x = MinMaxScaler()
scale_xv = MinMaxScaler()
x_scaled = scale_x.fit_transform(x_plot.reshape(-1, 1)).squeeze()
xv = scale_xv.fit_transform(xv_plot.reshape(-1, 1)).squeeze()
y0 = np.load('ratio_oil_to_injected_volumes.npy').reshape(-1, 1)
scale_y0 = MinMaxScaler()
y0_scaled = scale_y0.fit_transform(y0)
y_scaled = np.stack([y0_scaled.flatten()], axis=-1)

# Set the train and validation parts, https://stackoverflow.com/questions/61595081/validation-set-with-tensorflow-dataset
train_size = int(0.8 * x_scaled.shape[0]) #80 percent to train
x_train = x_scaled[:train_size]
y_train = y_scaled[:train_size]
x_val = x_scaled[train_size:]
y_val = y_scaled[train_size:]
train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
val_dataset = tf.data.Dataset.from_tensor_slices((x_val, y_val))

# design the neural network model
model = Sequential(
    [
        tf.keras.Input(shape=(1,)),
        # tf.keras.layers.BatchNormalization(),
        Dense(15, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(1),
    ]
) 

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor="loss", factor=0.1, patience=10, verbose=1, min_delta=1e-10
)
train_dataset = train_dataset.batch(10)
val_dataset = val_dataset.batch(10)
model.compile(loss="mse", optimizer=tf.keras.optimizers.Adam(learning_rate=0.1))
model.fit(train_dataset, epochs=100, verbose=1, callbacks=reduce_lr, validation_data=val_dataset)

test0 = np.array([row[0] for row in model(
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
# plot x vs yhat
pyplot.plot(x_plot, y0, '*', label="Data", markersize=5)
pyplot.plot(
    xv_plot,
    res0,
    label="Predicted",
    linestyle='-',
    linewidth=2,

)
pyplot.xlabel(r"Gas injection rate [stb/day]")
pyplot.ylabel(r"Recovered oil over injected volumes (gas + water) [-]")
pyplot.legend()
pyplot.savefig("ml_ratio_oil_to_injected_volumes.png", dpi=1200)
pyplot.show()
pyplot.close()