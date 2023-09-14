"""Transform keras models to an OPM format."""

import struct

import numpy as np

LAYER_DENSE = 1
LAYER_CONVOLUTION2D = 2
LAYER_FLATTEN = 3
LAYER_ELU = 4
LAYER_ACTIVATION = 5
LAYER_MAXPOOLING2D = 6
LAYER_LSTM = 7
LAYER_EMBEDDING = 8

ACTIVATION_LINEAR = 1
ACTIVATION_RELU = 2
ACTIVATION_SOFTPLUS = 3
ACTIVATION_SIGMOID = 4
ACTIVATION_TANH = 5
ACTIVATION_HARD_SIGMOID = 6


def write_dense(file, layer, write_activation):
    """
    Process the dense layer.
    """
    weights = layer.get_weights()[0]
    biases = layer.get_weights()[1]
    activation = layer.get_config()["activation"]

    file.write(struct.pack("I", LAYER_DENSE))
    file.write(struct.pack("I", weights.shape[0]))
    file.write(struct.pack("I", weights.shape[1]))
    file.write(struct.pack("I", biases.shape[0]))

    weights = weights.flatten()
    biases = biases.flatten()

    write_floats(file, weights)
    write_floats(file, biases)

    write_activation(activation)


def write_convolution2d(file, layer, write_activation):
    """
    Process the Convolution2D layer.
    """
    weights = layer.get_weights()[0]
    biases = layer.get_weights()[1]
    activation = layer.get_config()["activation"]

    # The kernel is accessed in reverse order. To simplify the C side we'll
    # flip the weight matrix for each kernel.
    weights = weights[:, :, ::-1, ::-1]

    file.write(struct.pack("I", LAYER_CONVOLUTION2D))
    file.write(struct.pack("I", weights.shape[0]))
    file.write(struct.pack("I", weights.shape[1]))
    file.write(struct.pack("I", weights.shape[2]))
    file.write(struct.pack("I", weights.shape[3]))
    file.write(struct.pack("I", biases.shape[0]))

    weights = weights.flatten()
    biases = biases.flatten()

    write_floats(file, weights)
    write_floats(file, biases)

    write_activation(activation)


def write_lstm(file, layer, write_activation):
    """
    Process the LSTM layer.
    """
    inner_activation = layer.get_config()["inner_activation"]
    activation = layer.get_config()["activation"]
    return_sequences = int(layer.get_config()["return_sequences"])

    weights = layer.get_weights()
    dic = {}
    dic["w_i"], dic["u_i"], dic["b_i"] = weights[0], weights[1], weights[2]
    dic["w_c"], dic["u_c"], dic["b_c"] = weights[3], weights[4], weights[5]
    dic["w_f"], dic["u_f"], dic["b_f"] = weights[6], weights[7], weights[8]
    dic["w_o"], dic["u_o"], dic["b_o"] = weights[9], weights[10], weights[11]

    file.write(struct.pack("I", LAYER_LSTM))
    file.write(struct.pack("I", dic["w_i"].shape[0]))
    file.write(struct.pack("I", dic["w_i"].shape[1]))
    file.write(struct.pack("I", dic["u_i"].shape[0]))
    file.write(struct.pack("I", dic["u_i"].shape[1]))
    file.write(struct.pack("I", dic["b_i"].shape[0]))

    file.write(struct.pack("I", dic["w_f"].shape[0]))
    file.write(struct.pack("I", dic["w_f"].shape[1]))
    file.write(struct.pack("I", dic["u_f"].shape[0]))
    file.write(struct.pack("I", dic["u_f"].shape[1]))
    file.write(struct.pack("I", dic["b_f"].shape[0]))

    file.write(struct.pack("I", dic["w_c"].shape[0]))
    file.write(struct.pack("I", dic["w_c"].shape[1]))
    file.write(struct.pack("I", dic["u_c"].shape[0]))
    file.write(struct.pack("I", dic["u_c"].shape[1]))
    file.write(struct.pack("I", dic["b_c"].shape[0]))

    file.write(struct.pack("I", dic["w_o"].shape[0]))
    file.write(struct.pack("I", dic["w_o"].shape[1]))
    file.write(struct.pack("I", dic["u_o"].shape[0]))
    file.write(struct.pack("I", dic["u_o"].shape[1]))
    file.write(struct.pack("I", dic["b_o"].shape[0]))

    for weight in dic:
        write_floats(file, weight.flatten())

    write_activation(inner_activation)
    write_activation(activation)
    file.write(struct.pack("I", return_sequences))


def write_floats(file, floats):
    """
    Writes floats to file in 1024 chunks.. prevents memory explosion
    writing very large arrays to disk when calling struct.pack().
    """
    step = 1024
    written = 0

    for i in np.arange(0, len(floats), step):
        remaining = min(len(floats) - i, step)
        written += remaining
        file.write(struct.pack(f"={remaining}f", *floats[i : i + remaining]))

    assert written == len(floats)


def export_model(model, filename):
    """
    Main routine.
    """
    with open(filename, "wb") as file:

        def write_activation(activation):
            if activation == "linear":
                file.write(struct.pack("I", ACTIVATION_LINEAR))
            elif activation == "relu":
                file.write(struct.pack("I", ACTIVATION_RELU))
            elif activation == "softplus":
                file.write(struct.pack("I", ACTIVATION_SOFTPLUS))
            elif activation == "tanh":
                file.write(struct.pack("I", ACTIVATION_TANH))
            elif activation == "sigmoid":
                file.write(struct.pack("I", ACTIVATION_SIGMOID))
            elif activation == "hard_sigmoid":
                file.write(struct.pack("I", ACTIVATION_HARD_SIGMOID))
            else:
                assert False, f"Unsupported activation type: {activation}"

        model_layers = [l for l in model.layers if type(l).__name__ not in ["Dropout"]]
        file.write(struct.pack("I", len(model_layers)))

        for layer in model_layers:
            layer_type = type(layer).__name__

            if layer_type == "Dense":
                write_dense(file, layer, write_activation)

            elif layer_type == "Convolution2D":
                assert (
                    layer.border_mode == "valid"
                ), "Only border_mode=valid is implemented"
                write_convolution2d(file, layer, write_activation)

            elif layer_type == "Flatten":
                file.write(struct.pack("I", LAYER_FLATTEN))

            elif layer_type == "ELU":
                file.write(struct.pack("I", LAYER_ELU))
                file.write(struct.pack("f", layer.alpha))

            elif layer_type == "Activation":
                activation = layer.get_config()["activation"]

                file.write(struct.pack("I", LAYER_ACTIVATION))
                write_activation(activation)

            elif layer_type == "MaxPooling2D":
                assert (
                    layer.border_mode == "valid"
                ), "Only border_mode=valid is implemented"

                pool_size = layer.get_config()["pool_size"]

                file.write(struct.pack("I", LAYER_MAXPOOLING2D))
                file.write(struct.pack("I", pool_size[0]))
                file.write(struct.pack("I", pool_size[1]))

            elif layer_type == "LSTM":
                write_lstm(file, layer, write_activation)

            elif layer_type == "Embedding":
                weights = layer.get_weights()[0]

                file.write(struct.pack("I", LAYER_EMBEDDING))
                file.write(struct.pack("I", weights.shape[0]))
                file.write(struct.pack("I", weights.shape[1]))

                weights = weights.flatten()

                write_floats(file, weights)

            else:
                assert False, f"Unsupported layer type: {layer_type}"
