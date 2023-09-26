"""Test that ``kerasify.py`` works and the models in OPM give the same results as in
``tf.keras``.


"""

import subprocess

import pytest

from pyopmnearwell.ml.kerasify import export_model

# @pytest.fixture(scope="session")
# def test_model(tensor, tmp_path: str):
#     model = tf.keras.Model()
#     model.initialize_random_parameters()
#     kerasify.save_model(model, os.path.join(tmp_path, "model.py"))

#     # Here, we call a ``command_line_evaluation`` binary that takes a model path and a
#     # tensor as command line arguments, loads the model in OPM, evaluates the tensor and
#     # returns the model output.

#     # For dense neural networks we can assume that the tensor is 1D, for convolutional
#     # neural networks there might need to be another method to load the tensor instead
#     # of passing it as a command line argument.
#     with subprocess.Popen([command_line_evaluation, path, tensor]) as proc:
#         cpp_evaluation = float(proc.stdout.read())
#     keras_evaluation = model(tensor)

#     assert cpp_evaluation == keras_evaluation
