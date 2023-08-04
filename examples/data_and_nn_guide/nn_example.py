"""Example on how to train a neural network on a dataset."""

import logging
import os

import matplotlib.pyplot as plt
import tensorflow as tf
from keras.layers import Dense, Input
from keras.models import Sequential

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# The following dataset was created using the ``pyopmnearlwell/ml/data.py`` script.
# It contains "SGAS" as input values and "PRESSURE" as target values (all timesteps and
# grid cells are flattened). The neural network will thus be trained to learn a function
# f(SGAS)=PRESSURE.
# Note: This is only a toy example to showcase ``tensorflow``
dirpath = os.path.split((os.path.realpath(__file__)))[0]
ds = tf.data.Dataset.load(os.path.join(dirpath, "ecl_dataset"))
# For some reason, we need to specify the batch size for the training algorithm at this
# point, instead of in ``model.fit`` as usual (see below).
ds = ds.batch(batch_size=100)
# We split the dataset into a training and a validation data set

train_size = int(0.95 * len(ds))
val_size = int(0.05 * len(ds))

train_ds = ds.take(train_size)
val_ds = ds.skip(val_size)

# We check the shape of the input and target tensors.
for x, y in train_ds:
    logger.info(f"shape of input tensor {x.shape}")
    logger.info(f"shape of output tensor {y.shape}")
    # logger.info(f"first input tensor {x}")
    # logger.info(f"first output tensor {y}")
    break

# Depending on the data, the inputs and targets might need to be scaled to values
# between 0 and 1 for the training of the model to work.
# Use ``sklearn.preprocessing.MinMaxScaler``, ``tf.keras.layers.BatchNormalization`` or
# other techniques for this.


# We specify the architecture of the neural network. We use a simple feedforward neural
# network with 5 fully connected layers of size 10. To stack them together, we use
# ``tf.keras.Sequential``. Furthermore, we specify the input shape and add a ``Dense``
# layer of size 1, that corresponds to the single output value we want the model to
# have.
model = Sequential(
    [
        Input(shape=(1,)),
        # Instead of initializing the input as a seperate layer, we could also pass the
        # input shape to the first layer:
        # Dense(10, activation="sigmoid", kernel_initializer="glorot_normal", input_shape=(1,)),
        # Actually, we don't need to specify the input shape at all, since tensorflow
        # will determine it automatically during training.
        Dense(10, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(10, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(10, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(10, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(10, activation="sigmoid", kernel_initializer="glorot_normal"),
        Dense(1),
    ]
)

# For more complicated models, define each layer manually and pass the output of the
# previous layer. At the end call ``tf.keras.Model`` on the inputs and outputs to create
# the model. This is a more flexible approach than ``tf.keras.Sequential``.
# Our model would look like the following
# inputs = Input(shape=(1,))
# x1 = Dense(10, activation="sigmoid", kernel_initializer="glorot_normal")(inputs)
# x2 = Dense(10, activation="sigmoid", kernel_initializer="glorot_normal")(x1)
# x3 = Dense(10, activation="sigmoid", kernel_initializer="glorot_normal")(x2)
# x4 = Dense(10, activation="sigmoid", kernel_initializer="glorot_normal")(x3)
# x5 = Dense(10, activation="sigmoid", kernel_initializer="glorot_normal")(x4)
# outputs = Dense(1)(x5)
# model = tf.keras.Model(inputs, outputs)

# We tell the training part of the model to reduce the mean squared error between its
# output and the target value (taken over a batch for each training step) and to use the
# Adam optimizer (a variation of gradient descent).
model.compile(
    loss="mse",
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.1),
)

# When the model gets stuck during training we want to reduce the learning rate. The
# following callback takes care of that. Note that we pass it to the ``model.fit``
# function.
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(
    monitor="loss", factor=0.1, patience=10, verbose=1, min_delta=1e-10
)
# There are more ways to decay the learning, e.g., using
# ``tf.keras.callbacks.LearningRateScheduler``.

# Save the model at the best epoch (ie.e, the best validation loss; another metric can
# be used to determine what is best).
checkpoint = tf.keras.callbacks.ModelCheckpoint(
    "bestmodel.{val_loss:.2f}",
    monitor="val_loss",
    verbose=1,
    save_best_only=True,
)


# For general tuning of hyperparameters such as learning rate, epochs, batchs_size etc.,
# make use of ``KerasTuner``
# https://keras.io/guides/keras_tuner/getting_started/


# Finally we call the ``model.fit`` function to train the model.
# At the end of the epoch, the loss on the validation data set will be computed.

# Note: Track performance on the validation data set, to make sure that the model is not
# overfitted to the training data. It might be useful to specify more metrics than just
# the loss.
model.fit(
    train_ds,
    epochs=5,
    verbose=1,
    callbacks=[checkpoint, reduce_lr],
    validation_data=val_ds,
)

# Since our dataset is already sepreated into input and target values, we can pass it to
# the ``.fit`` method which automatically determines the inputs and targets.
# If the data is only available as two ``numpy.ndarrays`` or ``tf.tensors`` of inputs
# ``x`` and targets ``y``, we would need to pass both:
# model.fit(x, y, epochs=100, batch_size=100, verbose=1, callbacks=reduce_lr)
# Note: In this case, we need to pass the batch size to ``model.fit`` instead of already
# specifying it in the dataset.


# Finally, we plot the trained model vs. the data
x, y = list(val_ds.as_numpy_iterator())[0]
y_hat = model(x)
# This is equivalent to ``model.predict(x)`` or ``model(x, training=False)``. Note that
# the output of the model might be different to training mode (i.e., to ``model(x,
# training=True)``), e.g., when a batch normalization layer is used.
plt.plot(x, y_hat, label="predict")
plt.scatter(x, y, label="data")
plt.legend()
plt.xlabel("PRESSURE")
plt.ylabel("SGAS")
plt.show()
