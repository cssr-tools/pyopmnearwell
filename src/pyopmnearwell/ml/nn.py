# pylint: skip-file
"""Transform ensemble data into datasets and train neural networks."""
from __future__ import annotations

import csv
import logging
import math
import pathlib
from functools import partial
from typing import Any, Literal, Optional, TypeAlias

import keras_tuner
import numpy as np
import pandas as pd
import tensorflow as tf
from pyopmnearwell.ml.kerasify import export_model
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ArrayLike: TypeAlias = tf.Tensor | np.ndarray


def get_FCNN(
    ninputs: int,
    noutputs: int,
    depth: int = 5,
    hidden_dim: int = 10,
    saved_model: Optional[str] = None,
    activation: Literal["sigmoid", "relu", "tanh"] = "sigmoid",
    kernel_initializer: Literal["glorot_normal", "glorot_uniform"] = "glorot_normal",
    normalization: bool = False,
) -> keras.Model:
    """Return a fully connected neural network with the specified architecture.

    Args:
        ninputs (int): Number of inputs to the model.
        noutputs (int): Number of outputs from the model.
        depth (int, optional): Number of hidden layers in the model. Defaults to 5.
        hidden_dim (int, optional): Number of neurons in each hidden layer. Defaults to
            10.
        saved_model (str, optional): Path to a saved model to load weights from.
            Defaults to None.
        activation (Literal["sigmoid", "relu", "tanh"], optional): Activation function
            to use in the hidden layers. Defaults to "sigmoid".
        kernel_initializer (Literal["glorot_normal", "glorot_uniform"], optional):
            Weight initialization method to use in the hidden layers. Defaults to
            "glorot_normal".
        normalization (bool, optional): Whether to use batch normalization in the model.
            Defaults to False.

    Returns:
        keras.Model: A fully connected neural network.

    """
    layers = [
        keras.layers.Dense(
            hidden_dim, activation=activation, kernel_initializer=kernel_initializer
        )
        for _ in range(depth)
    ]
    layers.insert(0, keras.layers.Input(shape=(ninputs,)))
    layers.append(keras.layers.Dense(noutputs))
    if normalization:
        layers.insert(1, keras.layers.Normalization())
        layers.append(keras.layers.Normalization(invert=True))
    model = keras.Sequential(layers)
    if saved_model is not None:
        model.load_weights(saved_model)
    return model


def get_RNN(
    ninputs: int,
    noutputs: int,
    units: int = 20,
    saved_model: Optional[str] = None,
    activation: Literal["sigmoid", "relu", "tanh"] = "tanh",
    kernel_initializer: Literal["glorot_normal", "glorot_uniform"] = "glorot_uniform",
) -> keras.Model:
    """Return a recurrent neural network with the specified architecture.

    Args:
        ninputs (int): Number of inputs to the model.
        noutputs (int): Number of outputs from the model.
        units (int, optional): Size of internal model state. Defaults to 20.
        hidden_dim (int, optional): Number of neurons in each hidden layer. Defaults to
            10.
        saved_model (str, optional): Path to a saved model to load weights from.
            Defaults to None.
        activation (Literal["sigmoid", "relu", "tanh"], optional): Activation function
            to use in the hidden layers. Defaults to "sigmoid".
        kernel_initializer (Literal["glorot_normal", "glorot_uniform"], optional):
            Weight initialization method to use in the hidden layers. Defaults to
            "glorot_normal".

    Returns:
        keras.Model: A fully connected neural network.

    """
    model: keras.Model = keras.Sequential()
    # RNN as model head.
    model.add(
        keras.layers.SimpleRNN(
            units,
            input_shape=(None, ninputs),
            return_sequences=True,
            activation=activation,
            kernel_initializer=kernel_initializer,
        )
    )
    # FCNN to as model tail.
    model.add(keras.layers.TimeDistributed(keras.layers.Dense(10, activation="relu")))
    model.add(keras.layers.TimeDistributed(keras.layers.Dense(10, activation="relu")))
    model.add(keras.layers.TimeDistributed(keras.layers.Dense(10, activation="relu")))
    model.add(keras.layers.Dense(noutputs))
    if saved_model is not None:
        model.load_weights(saved_model)
    return model


def get_GRU(
    ninputs: int,
    noutputs: int,
    units: int = 20,
    saved_model: Optional[str] = None,
    activation: Literal["sigmoid", "relu", "tanh"] = "tanh",
    kernel_initializer: Literal["glorot_normal", "glorot_uniform"] = "glorot_uniform",
) -> keras.Model:
    """Return a recurrent neural network with the specified architecture.

    Args:
        ninputs (int): Number of inputs to the model.
        noutputs (int): Number of outputs from the model.
        units (int, optional): Size of internal model state. Defaults to 20.
        hidden_dim (int, optional): Number of neurons in each hidden layer. Defaults to
            10.
        saved_model (str, optional): Path to a saved model to load weights from.
            Defaults to None.
        activation (Literal["sigmoid", "relu", "tanh"], optional): Activation function
            to use in the hidden layers. Defaults to "sigmoid".
        kernel_initializer (Literal["glorot_normal", "glorot_uniform"], optional):
            Weight initialization method to use in the hidden layers. Defaults to
            "glorot_normal".

    Returns:
        keras.Model: A fully connected neural network.

    """
    model: keras.Model = keras.Sequential()
    # RNN as model head.
    model.add(
        keras.layers.GRU(
            units,
            input_shape=(None, ninputs),
            return_sequences=True,
            activation=activation,
            kernel_initializer=kernel_initializer,
        )
    )
    # FCNN to as model tail.
    model.add(keras.layers.TimeDistributed(keras.layers.Dense(10, activation="relu")))
    model.add(keras.layers.TimeDistributed(keras.layers.Dense(10, activation="relu")))
    model.add(keras.layers.TimeDistributed(keras.layers.Dense(10, activation="relu")))
    model.add(keras.layers.Dense(noutputs))
    if saved_model is not None:
        model.load_weights(saved_model)
    return model


def get_LSTM(
    ninputs: int,
    noutputs: int,
    units: int = 20,
    saved_model: Optional[str] = None,
    activation: Literal["sigmoid", "relu", "tanh"] = "tanh",
    kernel_initializer: Literal["glorot_normal", "glorot_uniform"] = "glorot_uniform",
) -> keras.Model:
    """Return a recurrent neural network with the specified architecture.

    Args:
        ninputs (int): Number of inputs to the model.
        noutputs (int): Number of outputs from the model.
        units (int, optional): Size of internal model state. Defaults to 20.
        hidden_dim (int, optional): Number of neurons in each hidden layer. Defaults to
            10.
        saved_model (str, optional): Path to a saved model to load weights from.
            Defaults to None.
        activation (Literal["sigmoid", "relu", "tanh"], optional): Activation function
            to use in the hidden layers. Defaults to "sigmoid".
        kernel_initializer (Literal["glorot_normal", "glorot_uniform"], optional):
            Weight initialization method to use in the hidden layers. Defaults to
            "glorot_normal".

    Returns:
        keras.Model: A fully connected neural network.

    """
    model: keras.Model = keras.Sequential()
    # RNN as model head.
    model.add(
        keras.layers.LSTM(
            units,
            input_shape=(None, ninputs),
            return_sequences=True,
            activation=activation,
            kernel_initializer=kernel_initializer,
        )
    )
    # FCNN to as model tail.
    model.add(keras.layers.TimeDistributed(keras.layers.Dense(10, activation="relu")))
    model.add(keras.layers.TimeDistributed(keras.layers.Dense(10, activation="relu")))
    model.add(keras.layers.TimeDistributed(keras.layers.Dense(10, activation="relu")))
    model.add(keras.layers.Dense(noutputs))
    if saved_model is not None:
        model.load_weights(saved_model)
    return model


def scale_and_prepare_dataset(
    dsfile: str | pathlib.Path,
    feature_names: list[str],
    savepath: str | pathlib.Path,
    train_split: float = 0.9,
    val_split: Optional[float] = 0.1,
    test_split: Optional[float] = None,
    shuffle: Literal["first", "last", "false"] = "first",
    feature_range: tuple[float, float] = (-1, 1),
    target_range: tuple[float, float] = (-1, 1),
    scale: bool = True,
    **kwargs,
) -> (
    tuple[tuple[np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray]]
    | tuple[
        tuple[np.ndarray, np.ndarray],
        tuple[np.ndarray, np.ndarray],
        tuple[np.ndarray, np.ndarray],
    ]
):
    """Scale, shuffle and split a dataset.

    Args:
        dsfile (str | pathlib.Path): Dataset file.
        feature_names (list[str]): List of feature names.
        savepath (pathlib.Path): Savepath for the scaling values.
        train_split (float, optional): Train split. Defaults to 0.9.
        val_split (float, optional): Val split. Defaults to 0.1.
        test_split (float, optional): Test split. Defaults to None.
        shuffle (Literal["first", "last", "false"], optional): Options for shuffling the
            dataset:
            - "first": The dataset gets shuffled before the split.
            - "last": The dataset gets shuffled after the split.
            - "false": The dataset does not get shuffled.
            Defaults to "first".
        feature_range (tuple[float, float], optional): Target range of feature scaling.
            Defaults to (-1, 1).
        target_range (tuple[float, float], optional): Target range of target scaling.
            Defaults to (-1, 1)
        scale (bool, optional): Whether to scale the dataset. Defaults to True.

    Returns:
        tuple[tuple[np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray]]
        | tuple[
            tuple[np.ndarray, np.ndarray],
            tuple[np.ndarray, np.ndarray],
            tuple[np.ndarray, np.ndarray],
        ]: Tuple of scaled and split dataset. Includes test set only if
            ``test_split > 0``.

    """

    # Ensure ``savepath`` is a ``Path`` object.
    savepath = pathlib.Path(savepath)

    ds: tf.data.Dataset = tf.data.Dataset.load(str(dsfile))
    features, targets = next(iter(ds.batch(batch_size=len(ds)).as_numpy_iterator()))

    # Save feature and targets shape, e.g., for multidimensional data.
    features_shape: tuple = features.shape
    targets_shape: tuple = targets.shape
    # Reshape to one-dimensional data for the scalers to work.
    features = features.reshape(-1, features.shape[-1])
    targets = targets.reshape(-1, targets.shape[-1])

    if len(feature_names) > features.shape[-1]:
        raise ValueError("Too many feature names.")
    if len(feature_names) < features.shape[-1]:
        raise ValueError("Not all features are named.")

    # Infere values for ``val_split`` and test_split``.
    if val_split is None and test_split is None:
        val_split = 0.0
        test_split = 0.0
    elif val_split is None and test_split is not None:
        val_split = 1 - train_split - test_split
    elif val_split is not None and test_split is None:
        test_split = 1 - train_split - val_split

    # Some sanitizing of the splits. Have some tolerance to account for floating point
    # errors.
    abs_tol: float = 1e-5
    # Ignore mypy complaining that ``val_split`` and ``test_split`` can be None. The
    # lines above take care of that.
    if train_split + abs_tol < 0 or val_split + abs_tol < 0 or test_split + abs_tol < 0:  # type: ignore
        raise ValueError("Neither train, val not test split can be negative.")
    if not math.isclose(train_split + val_split + test_split, 1, abs_tol=abs_tol):  # type: ignore
        raise ValueError(
            "Train, val and test split do not add up to 1. If only train"
            + " split is specified, val and test split are set to 0."
        )
    logger.info(f"Train/val/test split is {train_split}/{val_split}/{test_split}")

    logger.info("Adapting MinMaxScalers")
    feature_scaler = MinMaxScaler(feature_range)
    target_scaler = MinMaxScaler(target_range)

    if scale:
        feature_scaler.fit(features)
        target_scaler.fit(targets)

    # Fit with ``feature_range``/``target_range`` for each feature/target to get no
    # scaling.
    else:
        feature_scaler.fit(
            np.linspace(
                np.full_like(features.shape[-1], feature_range[0]),
                np.full_like(features.shape[-1], feature_range[1]),
                2,
                axis=0,
            )
        )
        target_scaler.fit(
            np.linspace(
                np.full_like(features.shape[-1], feature_range[0]),
                np.full_like(features.shape[-1], feature_range[1]),
                2,
                axis=0,
            )
        )

    with (savepath / "scalings.csv").open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["variable", "min", "max"])
        writer.writeheader()
        for feature_name, feature_min, feature_max in zip(
            feature_names, feature_scaler.data_min_, feature_scaler.data_max_
        ):
            writer.writerow(
                {
                    "variable": f"input_{feature_name}",
                    "min": feature_min,
                    "max": feature_max,
                }
            )
        writer.writerow(
            {
                "variable": "output_WI",
                "min": target_scaler.data_min_[0],
                "max": target_scaler.data_max_[0],
            }
        )
        writer.writerow(
            {
                "variable": "feature_range",
                "min": feature_range[0],
                "max": feature_range[1],
            }
        )
        writer.writerow(
            {
                "variable": "target_range",
                "min": target_range[0],
                "max": target_range[1],
            }
        )
    logger.info(f"Saved scalings to {savepath / 'scalings.csv'}")

    # Reload the dataset and shuffle once before splitting.
    ds = tf.data.Dataset.load(str(dsfile))
    if shuffle == "first":
        logger.info("Shuffling the dataset (before splitting)")
        # Do not ``reshuffle_each_iteration`` s.t. take and skip applies to the same
        # shuffle order.
        ds = ds.shuffle(
            buffer_size=max([len(ds), kwargs.get("buffer_size", len(ds))]),
            reshuffle_each_iteration=False,
        )

    # Split the dataset.
    # Ignore mypy complaining that ``val_split`` and ``test_split`` can be None.
    logger.info("Splitting data into train/val/test dataset")
    train_size = round(train_split * len(ds))  # type: ignore
    val_size = round(val_split * len(ds))  # type: ignore
    train_ds = ds.take(train_size)
    val_ds = ds.skip(train_size).take(val_size)
    test_ds = ds.skip(train_size).skip(val_size)

    # Treat the other two shuffle options.
    if shuffle == "last":
        logger.info("Shuffling the dataset (after splitting)")
        train_ds, val_ds, test_ds = [
            partial_ds.shuffle(
                buffer_size=max(
                    [len(partial_ds), kwargs.get("buffer_size", len(partial_ds))]
                )
            )
            for partial_ds in [train_ds, val_ds, test_ds]
        ]

    elif shuffle == "false":
        logger.info("The dataset was not shuffled")

    train_features, train_targets = next(
        iter(train_ds.batch(batch_size=len(train_ds)).as_numpy_iterator())
    )
    # Ensure that the program works for a val split of 0.0.
    # Ignore mypy complaining that ``val_split`` can be None.
    if val_split > 0:  # type: ignore
        val_features, val_targets = next(
            iter(val_ds.batch(batch_size=len(val_ds)).as_numpy_iterator())
        )
    else:
        val_features, val_targets = np.zeros((1, train_features.shape[-1])), np.zeros(
            (1, train_targets.shape[-1])
        )

    # Reshape to one-dimensional data.
    train_features = train_features.reshape(-1, features_shape[-1])
    train_targets = train_targets.reshape(-1, targets_shape[-1])
    val_features = val_features.reshape(-1, features_shape[-1])
    val_targets = val_targets.reshape(-1, targets_shape[-1])

    # Scale the features and targets.
    logger.info("Scaling data")
    train_features = feature_scaler.transform(train_features)
    train_targets = target_scaler.transform(train_targets)
    val_features = feature_scaler.transform(val_features)
    val_targets = target_scaler.transform(val_targets)

    # Reshape to original shape
    train_features = train_features.reshape(-1, *features_shape[1:])
    train_targets = train_targets.reshape(-1, *targets_shape[1:])
    val_features = val_features.reshape(-1, *features_shape[1:])
    val_targets = val_targets.reshape(-1, *targets_shape[1:])

    # Only return test ds if ``test_split > 0``.
    # Ignore mypy complaining that ``test_split`` can be None.
    if test_split > 0:  # type: ignore
        test_features, test_targets = next(
            iter(test_ds.batch(batch_size=len(test_ds)).as_numpy_iterator())
        )
        test_features = test_features.reshape(-1, features_shape[-1])
        test_targets = test_targets.reshape(-1, targets_shape[-1])

        test_features = feature_scaler.transform(test_features)
        test_targets = target_scaler.transform(test_targets)

        test_features = test_features.reshape(-1, *features_shape[1:])
        test_targets = test_targets.reshape(-1, *targets_shape[1:])

        return (
            (train_features, train_targets),
            (val_features, val_targets),
            (test_features, test_targets),
        )

    return (train_features, train_targets), (val_features, val_targets)


def train(
    model: keras.Model,
    train_data: tuple[ArrayLike, ArrayLike],
    val_data: tuple[ArrayLike, ArrayLike],
    savepath: str | pathlib.Path,
    lr: float = 0.1,
    epochs: int = 500,
    bs: int = 64,
    patience: int = 100,
    lr_patience: int = 10,
    kerasify: bool = True,
    loss_func: Literal[
        "mse", "MeanAbsolutePercentageError", "MeanSquaredLogarithmicError"
    ] = "mse",
    recompile_model: bool = True,
    **kwargs,
) -> None:
    """Train a tensorflow model on the provided training data and save the best model.

    Args:
        model (tf.Module): Model to be trained.
        train_data (tuple[ArrayLike, ArrayLike]): Training features and targets.
        val_data (tuple[ArrayLike, ArrayLike]): Validation features and targets.
        savepath (pathlib.Path): Savepath for models and logging.
        lr (float, optional): Initial learning rate. Defaults to 0.1.
        epochs (_type_, optional): Training epochs. Defaults to 500.
        bs (int, optional): Batch size. Defaults to 64.
        patience (int, optional): Number of epochs without improvement before early
            stopping. Defaults to 100.
        lr_patience (int, optional): Number of epochs without improvement before lr
            decay. Defaults to 10.
        kerasify (bool, optional): Export the best model with kerasify after training.
            Defaults to True.
        loss_func (Literal["mse", "MeanAbsolutePercentageError",
            "MeanSquaredLogarithmicError"], optional): Loss function. Defaults to "mse".
        recompile_model (bool, optional): Whether to recompile the model before
            training. Can e.g., be set to false, if the model is built and compiled by a
            different function. Defaults to True.
        **kwargs: Get passed to the ``model.fit()`` method.

    Returns:
        None

    """
    # Ensure ``savepath`` is a ``Path`` object.
    savepath = pathlib.Path(savepath)

    train_features, train_targets = train_data
    val_features, val_targets = val_data

    # Callbacks for model saving, learning rate decay and logging.
    checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
        savepath / "bestmodel",
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
            # min_lr=1e-7,
        ),
    )
    early_stopping_callback = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss",
        patience=patience,
        verbose=1,
    )
    tensorboard_callback = tf.keras.callbacks.TensorBoard(
        log_dir=str(savepath / "logdir")
    )

    if recompile_model:
        if loss_func == "mse":
            loss: keras.losses.Loss = keras.losses.MeanSquaredError()
        elif loss_func == "MeanAbsolutePercentageError":
            loss = keras.losses.MeanAbsolutePercentageError()
        elif loss_func == "MeanSquaredLogarithmicError":
            loss = keras.losses.MeanSquaredLogarithmicError()
        model.compile(
            loss=loss,
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
        callbacks=[
            checkpoint_callback,
            lr_callback,
            early_stopping_callback,
            tensorboard_callback,
        ],
        **kwargs,
    )
    model.save_weights(savepath / "finalmodel")

    # Load the best model and save to OPM format.
    model.load_weights(savepath / "bestmodel")
    model.save(savepath / "bestmodel.keras")
    if kerasify:
        export_model(model, savepath / "WI.model")


def build_model(
    hp: keras_tuner.HyperParameters,
    ninputs: int,
    noutputs: int,
    lr_tune: float = 0.1,
) -> tf.Module:
    """Build and compile a FCNN with the given hyperparameters.

    Args:
        hp (keras_tuner.Hyperparameters): Hyperparameters object.
        ninputs (int): Number of inputs.
        noutputs (int): Number of outputs.

    Returns:
        tf.Module: The built neural network model.

    """
    # Get hyperparameters.
    # depth: int = hp.Int("depth", min_value=3, max_value=20, step=2)
    depth: int = hp.Int("depth", min_value=3, max_value=6, step=2)
    hidden_size: int = hp.Int("hidden_size", min_value=5, max_value=50, step=5)
    activation: Literal["sigmoid", "relu", "tanh"] = hp.Choice(
        "activation", ["sigmoid", "relu", "tanh"]
    )
    loss_func: str = hp.Choice("loss", ["mse"])
    if loss_func == "mse":
        loss: keras.losses.Loss = keras.losses.MeanSquaredError()
    elif loss_func == "MeanAbsolutePercentageError":
        loss = keras.losses.MeanAbsolutePercentageError()
    elif loss_func == "MeanSquaredLogarithmicError":
        loss = keras.losses.MeanSquaredLogarithmicError()

    # Build model.
    model: keras.Model = get_FCNN(
        ninputs=ninputs,
        noutputs=noutputs,
        depth=depth,
        hidden_dim=hidden_size,
        activation=activation,
    )
    model.compile(
        loss=loss,
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr_tune),
    )
    return model


def tune(
    ninputs: int,
    noutputs: int,
    train_data: tuple[ArrayLike, ArrayLike],
    val_data: tuple[ArrayLike, ArrayLike],
    savepath: str | pathlib.Path,
    objective: Literal["loss", "val_loss"] = "val_loss",
    max_trials: int = 5,
    executions_per_trial: int = 1,
    sample_weight: ArrayLike = np.array([1.0]),
    lr_tune: float = 0.1,
    **kwargs,
) -> tuple[keras.Model, keras_tuner.Tuner]:
    """
    Tune the hyperparameters of a neural network model using random search.

    Args:
        ninputs (int): Number of input features to the model.
        noutputs (int): Number of output features to the model.
        train_data (tuple[ArrayLike, ArrayLike]): Tuple of training input and target
            data.
        val_data (tuple[ArrayLike, ArrayLike],): Tuple of validation input and target
            data.
        objective (Literal["loss", "val_loss"], optional): Objective for search.
            Defaults to ``"val_loss"``.
        max_trials (int): Default is 5.
        executions_per_trial (int): Default is 1.
        sample_weight:(ArrayLike): Default is ``np.array([1.0])``.
        **kwargs: Get passed to the tuner's search method.

    Returns:
        tf.Module: The model compiled with the best hyperparameters.
        keras_tuner.Tuner: The tuner.

    Raises:
        ValueError: If `train_data` or `val_data` is not a tuple of two tensors.

    """
    # Define the tuner and start a search.
    tuner = keras_tuner.RandomSearch(
        hypermodel=partial(
            build_model,
            ninputs=ninputs,
            noutputs=noutputs,
            lr_tune=lr_tune,
        ),
        objective=objective,
        max_trials=max_trials,
        executions_per_trial=executions_per_trial,
        overwrite=True,
        directory=savepath,
        project_name="tuner",
        **kwargs,
    )
    tuner.search_space_summary()

    if not isinstance(train_data, tuple) or len(train_data) != 2:
        raise ValueError("train_data must be a tuple of two tensors.")
    if not isinstance(val_data, tuple) or len(val_data) != 2:
        raise ValueError("val_data must be a tuple of two tensors.")

    # If kwargs contains epochs, this will fail.
    tuner.search(
        train_data[0],
        train_data[1],
        epochs=20,
        validation_data=val_data,
        sample_weight=sample_weight,
        **kwargs,
    )
    tuner.results_summary()

    # Build the model with the best hp.
    best_hps = tuner.get_best_hyperparameters(5)
    model = build_model(best_hps[0], ninputs, noutputs)

    return model, tuner


def save_tune_results(tuner: keras_tuner.Tuner, savepath: str | pathlib.Path) -> None:
    # Ensure ``savepath`` is a ``Path`` object.
    savepath = pathlib.Path(savepath)

    trials: list[keras_tuner.engine.trial.Trial] = tuner.oracle.get_best_trials(
        num_trials=tuner.oracle.max_trials
    )
    hp_list: list[dict[str, Any]] = []
    for trial in trials:
        hp_list.append(
            trial.hyperparameters.get_config()["values"] | {"Score": trial.score}
        )
    pd.DataFrame(hp_list).to_csv(
        str(savepath / "tuner_results.csv"), na_rep="Missing", index=False
    )


def scale_and_evaluate(
    model: keras.Model,
    model_input: ArrayLike,
    scalingsfile: str | pathlib.Path,
) -> tf.Tensor:
    """Scale the input, evaluate with the model and scale the output.

    Args:
        model (tf.keras.Model): A Keras model to evaluate the input with.
        model_input (ArrayLike): Input tensor. Can be a batch.
        scalingsfile (str | pathlib.Path): The path to the CSV file containing the
            scaling parameters for MinMaxScaling.

    Returns:
        tf.Tensor: The model's output, scaled back to the original range.

    Raises:
        FileNotFoundError: If ``scalingsfile`` does not exist.
        ValueError: If ``scalingsfile`` contains an invalid row.

    """
    # Ensure ``ensemble_path`` is a ``Path`` object.
    scalingsfile = pathlib.Path(scalingsfile)

    # Get the feature and target scaling.
    feature_min: list[float] = []
    feature_max: list[float] = []
    target_min: list[float] = []
    target_max: list[float] = []
    feature_range: list[float] = [-1.0, 1.0]
    target_range: list[float] = [-1.0, 1.0]
    with scalingsfile.open("r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=["variable", "min", "max"])

        # Skip the header
        next(reader)

        for row in reader:
            if row["variable"].startswith("output"):
                target_min.append(float(row["min"]))
                target_max.append(float(row["max"]))
            elif row["variable"].startswith("input"):
                feature_min.append(float(row["min"]))
                feature_max.append(float(row["max"]))
            elif row["variable"] == "feature_range":
                feature_range[0] = float(row["min"])
                feature_range[1] = float(row["max"])
            elif row["variable"] == "target_range":
                target_range[0] = float(row["min"])
                target_range[1] = float(row["max"])
            else:
                raise ValueError("Name of scaling variable is invalid.")

    # Create MinMaxScalers and manually set the parameters.
    feature_scaler: MinMaxScaler = MinMaxScaler(feature_range)
    feature_scaler.data_min_ = np.array(feature_min)
    feature_scaler.data_max_ = np.array(feature_max)
    feature_scaler.scale_ = (
        feature_range[1] - feature_range[0]
    ) / handle_zeros_in_scale(feature_scaler.data_max_ - feature_scaler.data_min_)
    feature_scaler.min_ = (
        feature_range[0] - feature_scaler.data_min_ * feature_scaler.scale_
    )
    target_scaler: MinMaxScaler = MinMaxScaler(target_range)
    target_scaler.data_min_ = np.array(target_min)
    target_scaler.data_max_ = np.array(target_max)
    target_scaler.scale_ = (target_range[1] - target_range[0]) / handle_zeros_in_scale(
        target_scaler.data_max_ - target_scaler.data_min_
    )
    target_scaler.min_ = (
        target_range[0] - target_scaler.data_min_ * target_scaler.scale_
    )

    # Save feature and targets shape and reshape to one-dimensional data, e.g., for
    # multidimensional data. The scaler accepts at most two dimensions.
    input_shape: tuple = model_input.shape
    model_input = model_input.reshape(-1, input_shape[-1])

    scaled_input: np.ndarray = feature_scaler.transform(model_input)
    scaled_input = scaled_input.reshape(input_shape)

    # Run model.
    output: tf.Tensor = model(scaled_input)

    output_shape: tuple = output.shape
    output = tf.reshape(output, (-1, output_shape[-1]))

    unscaled_output: tf.Tensor = target_scaler.inverse_transform(output)
    unscaled_output = tf.reshape(unscaled_output, output_shape)

    return unscaled_output


def handle_zeros_in_scale(scale: ArrayLike) -> np.ndarray:
    """Set scales of near constant features to 1.

    Note: This behavior is in line with `sklearn.preprocessing.MinMaxScaler`.

    Args:
        scale (ArrayLike): The scale array.

    Returns:
        np.ndarray: The modified scale array.

    """
    # ``atol`` must be very low s.t. this works for permeability in [m^2] for example.
    return np.where(np.isclose(scale, 0.0, atol=1e-20), np.ones_like(scale), scale)
