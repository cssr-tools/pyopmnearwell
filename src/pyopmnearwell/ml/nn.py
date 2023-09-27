"""Transform ensemble data into datasets and train neural networks."""
from __future__ import annotations

import csv
import logging
import os
from typing import Literal, Optional

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.models import Sequential

import pyopmnearwell.utils.units as units
from pyopmnearwell.ml.kerasify import export_model
from pyopmnearwell.utils.formulas import peaceman_WI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_FCNN(
    ninputs: int,
    noutputs: int,
    depth: int = 5,
    hidden_dim: int = 10,
    saved_model: Optional[str] = None,
) -> tf.Module:
    layers = [
        Dense(hidden_dim, activation="sigmoid", kernel_initializer="glorot_normal")
        for _ in range(depth)
    ]
    layers.insert(0, Input(shape=(ninputs,)))
    layers.append(Dense(noutputs))
    model = Sequential(layers)
    if saved_model is not None:
        model.load_weights(saved_model)
    return model


def scale_and_prepare_dataset(
    dsfile: str,
    feature_names: list[str],
    savepath: str,
    train_split: float = 0.9,
    val_split: Optional[float] = None,
) -> tuple[tuple[np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray]]:
    ds: tf.data.Dataset = tf.data.Dataset.load(dsfile)
    features, targets = next(iter(ds.batch(batch_size=len(ds)).as_numpy_iterator()))
    if len(feature_names) > features.shape[-1]:
        raise ValueError("Too many feature names.")
    elif len(feature_names) < features.shape[-1]:
        raise ValueError("Not all features are named.")
    if val_split is None:
        val_split = 1 - train_split
    elif train_split + val_split != 1:
        raise ValueError("Train and val split does not add up to 1.")
    logger.info("Adapt MinMaxScalers")
    feature_scaler = MinMaxScaler()
    target_scaler = MinMaxScaler()
    feature_scaler.fit(features)
    target_scaler.fit(targets)
    with open(os.path.join(savepath, "scales.csv"), "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["variable", "min", "max"])
        writer.writeheader()
        for feature_name, feature_min, feature_max in zip(
            feature_names, feature_scaler.data_min_, feature_scaler.data_max_
        ):
            writer.writerow(
                {"variable": feature_name, "min": feature_min, "max": feature_max}
            )
        writer.writerow(
            {
                "variable": "WI",
                "min": target_scaler.data_min_[0],
                "max": target_scaler.data_max_[0],
            }
        )
    logger.info(f"Saved scalings to {os.path.join(savepath, 'scales.csv')}.")

    # Reload the dataset and shuffle once before splitting into training and val.
    ds = tf.data.Dataset.load(dsfile)
    ds = ds.shuffle(buffer_size=len(ds))

    # Split the dataset into a training and a validation data set.
    train_size = int(train_split * len(ds))
    val_size = int(val_split * len(ds))
    train_ds = ds.take(train_size)
    val_ds = ds.skip(train_size)

    train_features, train_targets = next(
        iter(train_ds.batch(batch_size=len(train_ds)).as_numpy_iterator())
    )
    val_features, val_targets = next(
        iter(val_ds.batch(batch_size=len(val_ds)).as_numpy_iterator())
    )
    # Scale the features and targets.
    train_features = feature_scaler.transform(train_features)
    train_targets = target_scaler.transform(train_targets)
    val_features = feature_scaler.transform(val_features)
    val_targets = target_scaler.transform(val_targets)
    logger.info(f"Scaled data and split into training and validation dataset.")
    return (train_features, train_targets), (val_features, val_targets)


def l2_error(
    target: tf.Tensor, prediction: tf.Tensor, mode: Literal["relative", "max"]
) -> tf.Tensor:
    """Calculate the relative L2 error between the target and prediction.



    Parameters:
        target: _description_
        prediction: _description_

    Returns:
        _description_
    """
    pass


def train(
    model: tf.Module,
    train_data: tuple[tf.Tensor, tf.Tensor],
    val_data: tuple[tf.Tensor, tf.Tensor],
    savepath: str,
    lr: float = 0.1,
    epochs: int = 500,
    bs: int = 64,
    patience: int = 20,
    lr_patience: int = 10,
) -> None:
    train_features, train_targets = train_data
    val_features, val_targets = val_data

    # Callbacks for model saving, learning rate decay and logging.
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        os.path.join(savepath, "bestmodel"),
        monitor="val_loss",
        verbose=1,
        save_best_only=True,
        save_weights_only=True,
    )
    lr_callback = (
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="loss",
            factor=0.1,
            patience=lr_patience,
            verbose=1,
            min_delta=1e-10,
            min_lr=1e-7,
        ),
    )
    tensorboard_callback = tf.keras.callbacks.TensorBoard(
        log_dir=os.path.join(savepath, "logdir")
    )

    # Train the model.
    model.compile(
        loss="mse",
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
    )
    model.fit(
        train_features,
        train_targets,
        batch_size=bs,
        epochs=epochs,
        # Ignore Pylance complaining. This is an typing error in tensorflow/keras.
        verbose=1,  # type: ignore
        validation_data=(val_features, val_targets),
        callbacks=[checkpoint_callback, lr_callback, tensorboard_callback],
    )
    model.save_weights(os.path.join(savepath, "finalmodel"))

    # Load the best model and save to OPM format.
    model.load_weights(os.path.join(savepath, "bestmodel"))
    export_model(model, os.path.join(savepath, "WI.model"))


# # Plot the trained model vs. the data.
# # Sample from the unshuffled data set to have the elements sorted.
# features, targets = next(
#     iter(orig_ds.batch(batch_size=len(orig_ds)).as_numpy_iterator())
# )

# # loop through 3 time steps and 3 three pressures
# features = features.reshape((runspecs.NPOINTS, 395, ninputs))[:3, ...]
# targets = targets.reshape((runspecs.NPOINTS, 395, noutputs))[:3, ...]

# OPM_ML: str = "/home/peter/Documents/2023_CEMRACS/opm_ml"
# CO2BRINEPVT: str = os.path.join(OPM_ML, "build/opm-common/bin/co2brinepvt")

# for feature, target in list(zip(features, targets)):
#     plt.figure()
#     target_hat = target_scaler.inverse_transform(
#         model(feature_scaler.transform(feature))
#     )
#     # Calculate density and viscosity
#     with subprocess.Popen(
#         [
#             CO2BRINEPVT,
#             "density",
#             "brine",
#             str(feature[0, 0]),
#             str(runspecs.TEMPERATURE + units.CELSIUS_TO_KELVIN),
#         ],
#         stdout=subprocess.PIPE,
#     ) as proc:
#         density: float = float(proc.stdout.read())
#     with subprocess.Popen(
#         [
#             CO2BRINEPVT,
#             "viscosity",
#             "brine",
#             str(feature[0, 0]),
#             str(runspecs.TEMPERATURE + units.CELSIUS_TO_KELVIN),
#         ],
#         stdout=subprocess.PIPE,
#     ) as proc:
#         viscosity: float = float(proc.stdout.read())
#     # Calculate analytical WI.
#     peaceman = (
#         np.vectorize(peaceman_WI)(
#             runspecs.PERMEABILITY * units.MILIDARCY_TO_M2,
#             feature[..., 1],
#             runspecs.WELL_RADIUS,
#             density,
#             viscosity,
#         )
#         / runspecs.SURFACE_DENSITY
#     )
#     plt.plot(
#         feature[..., 1].flatten(),
#         target_hat,
#         label="nn",
#     )
#     plt.plot(
#         feature[..., 1].flatten(),
#         peaceman,
#         label="Peaceman",
#     )
#     plt.scatter(
#         feature[..., 1].flatten()[::5],
#         target.flatten()[::5],
#         label="data",
#     )
#     plt.legend()
#     plt.title(rf"$p_i={feature[20][0]:.3e}\,[Pa]$ at $r={feature[300][1]:.2f}\,[m]$")
#     plt.xlabel(r"$r\,[m]$")
#     plt.ylabel(r"$WI\,[m^4\cdots/kg]$")
#     plt.savefig(
#         os.path.join(
#             savepath, f"nn_p_r_to_WI_p_{feature[300][0]:.3e}_t_{feature[0][1]:0f}.png"
#         )
#     )
#     plt.show()
