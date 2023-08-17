import numpy as np
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

tf.keras.utils.set_random_seed(42)

TINJ = 365
TSTOP = 90
TOPER = 70
TASSES = 28

# Scale the x and y data
x_for_ml_plot = np.linspace(TINJ+TSTOP, TINJ+TSTOP+TOPER+TASSES, 100)
x_all = np.load('times_998.npy')
x_sort_indx = np.argsort(x_all)
x_all = np.sort(x_all)
x0 = x_all[x_all < TINJ+TSTOP+TOPER] # Keep only the data before the assessment
scale_x = MinMaxScaler()
x_all_scaled = scale_x.fit_transform(x_all.reshape(-1, 1)).squeeze()
x_scaled = scale_x.transform(x0.reshape(-1,1))
y_all = np.load('fgpt_998.npy')[x_sort_indx].reshape(-1, 1)
y0 = y_all[x_all < TINJ+TSTOP+TOPER] # Keep only the data before the assessment

scale_y0 = MinMaxScaler()
y_all_scaled = scale_y0.fit_transform(y_all)
y0_scaled = scale_y0.transform(y0.reshape(-1,1))
y_scaled = np.stack([y0_scaled.flatten()], axis=-1)

# Set the train and validation parts, https://stackoverflow.com/questions/61595081/validation-set-with-tensorflow-dataset
train_size = int(.8 * x_scaled.shape[0]) #95 percent to train
x_train = x_scaled[:train_size]
y_train = y_scaled[:train_size]
x_val = x_scaled[train_size:]
y_val = y_scaled[train_size:]
train_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
val_dataset = tf.data.Dataset.from_tensor_slices((x_val, y_val))

# Design the neural network model, see https://machinelearningmastery.com/time-series-prediction-with-deep-learning-in-python-with-keras/
look_back = 1
model = Sequential()
model.add(tf.keras.Input(shape=(1,)))
model.add(Dense(100, activation='relu', kernel_initializer=tf.keras.initializers.GlorotUniform(seed=None)))
model.add(Dense(100, activation='relu', kernel_initializer=tf.keras.initializers.GlorotUniform(seed=None)))
model.add(Dense(1))
train_dataset = train_dataset.batch(len(x_train))
val_dataset = val_dataset.batch(len(x_val))
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor="loss", factor=0.5, patience=20, verbose=1, min_delta=1e-10
)
model.compile(loss="mse", optimizer=tf.keras.optimizers.Adam())
model.fit(train_dataset, epochs=25000, verbose=1, validation_data=val_dataset)

y_ml = np.array([row[0] for row in model(
                np.stack(
                    [
                        scale_x.transform(x_for_ml_plot.reshape(-1,1)),
                    ],
                    axis=-1,
                )
            )])

mse = tf.keras.losses.MeanSquaredError()

# Plot the results
y_for_ml_plot = scale_y0.inverse_transform(
            y_ml.reshape(-1,1)
        )
plt.plot(x_all[x_all < TINJ+TSTOP+TOPER], y_all[x_all < TINJ+TSTOP+TOPER], '*', label="Data for ML", markersize=5, color = 'g')
plt.plot(x_all[x_all >= TINJ+TSTOP+TOPER], y_all[x_all >= TINJ+TSTOP+TOPER], '*', label="Data to assess the ML", markersize=5, color = 'r')
plt.plot(
    x_for_ml_plot[x_for_ml_plot < TINJ+TSTOP+TOPER],
    y_for_ml_plot[x_for_ml_plot < TINJ+TSTOP+TOPER],
    label="Trained ML",
    linestyle='-',
    linewidth=2,
    color = 'k',
)
plt.plot(
    x_for_ml_plot[x_for_ml_plot >= TINJ+TSTOP+TOPER],
    y_for_ml_plot[x_for_ml_plot >= TINJ+TSTOP+TOPER],
    label="Forecast ML",
    linestyle='--',
    linewidth=2,
    color = 'k',
)
plt.axvline(x = TINJ+TSTOP+TOPER, linestyle='dotted', color = 'k')
plt.ylabel(r"Produced H$_2$ [sm${^3}$]")
plt.xlabel(r"Time to assess the operation [d]")
plt.legend()
plt.savefig("ml_fgpt.png", dpi=1200)
plt.show()
plt.close()