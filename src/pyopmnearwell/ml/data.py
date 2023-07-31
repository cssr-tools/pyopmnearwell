"""This module provides functionality to parse ``*.UNRST`` files for given keywords and
transform the extracted values into a tensorflow dataset.

Note: Some manual changes are needed if the tensors of the dataset shall have a shape
different from the default one. The lines that need to be changed are marked with 
# MANUAL CHANGES.

"""
from __future__ import annotations

import argparse
import logging
import os
import random
from typing import Literal, Optional

import numpy as np
import tensorflow as tf
from ecl.eclfile.ecl_file import EclFile, open_ecl_file

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class EclDataSet:
    """Generate samples for a ``tf.data.Dataset`` from a folder of ``*.UNRST`` files.

    Example:
        After instantiation of the class, it can be passed to
        ``tf.data.Dataset.from_generator()``, to create a dataset that ``tensorflow``
        can work with.
        >>> data = EclDataSet(path, input_kws, target_kws)
        >>> data.read_data()
        >>> ds = tf.data.Dataset.from_generator(
        >>>     data,
        >>>     output_signature=(tf.TensorSpec(), tf.TensorSpec())
        >>> )

        To save the dataset, use
        >>> ds.save(path)
        Afterwards, the ``*.UNRST`` files used to generated the dataset can be deleted.

    """

    inputs: tf.Tensor
    """Stores all inputs of the dataset.

    ``shape=(num_files, num_report_steps, num_cells, len(input_kws))``

    """
    targets: tf.Tensor
    """Stores all targets of the dataset.

    ``shape=(num_files, num_report_steps, num_cells, len(target_kws))``

    """

    def __init__(
        self,
        path: str,
        input_kws: list[str],
        target_kws: list[str],
        file_format: Literal["ecl", "opm"] = "ecl",
        dtype=tf.float32,
        shuffle_on_epoch_end: bool = False,
        read_data_on_init: bool = True,
    ) -> None:
        """Initiate the class.

        Parameters:
            path: _description_
            input_kws: Keywords for attributes of the ``EclFile`` that shall become
                model input.
            target_kws: Keywords for attributes of the ``EclFile`` that shall become
                targets for model training.
            type: _description_. Defaults to ``"ecl"``.
            read_data_on_init: Reads data from ``*.UNRST`` files in ``path`` on
                instantiation. Disable for testing/debugging. Defaults to ``True``.


        Warning:
            As of now, ``type`` is always assumed to be ``ecl``. ``opm`` is not
            implemented yet.

        Returns:
            _description_

        """
        self.path: str = path
        self.input_kws: list[str] = input_kws
        self.target_kws: list[str] = target_kws
        self.dtype = dtype
        if read_data_on_init:
            self.read_data()
        self.shuffle_on_epoch_end: bool = shuffle_on_epoch_end

    def read_data(self):
        """Create a ``tensorflow`` dataset from a folder of ``ecl`` or ``opm`` files."""
        logger.info("Generating datapoints...")
        _inputs_lst: list[tf.Tensor] = []
        _targets_lst: list[tf.Tensor] = []
        for filename in os.listdir(self.path):
            if filename.endswith("UNRST"):
                with open_ecl_file(os.path.join(self.path, filename)) as ecl_file:
                    try:
                        input, target = self.EclFile_to_datapoint(ecl_file)
                        _inputs_lst.append(input)
                        _targets_lst.append(target)
                        logger.info(f"Generated a datapoint from {filename}.")
                    except KeyError as e:
                        logger.info(f"{filename} has no keyword {e}.")
                        continue
        if len(_inputs_lst) > 0 and len(_targets_lst) > 0:
            # Transform the lists into a tensor

            # MANUAL CHANGES: Change the lines below to change what becomes part of the
            # batch dimension and what becomes part of the input dimension.
            self.inputs = tf.stack(_inputs_lst, axis=0)
            # ``shape=(num_files, num_report_steps, num_cells, len(input_kws))``
            self.targets = tf.stack(_targets_lst, axis=0)
            # ``shape=(num_files, num_report_steps, num_cells, len(target_kws))``
        else:
            self.inputs = tf.zeros((1, 1))
            self.targets = tf.zeros((1, 1))
            logger.info(
                """Not able to extract keywords from input files. Check if there are
                input files in the folder that contain the given keywords.

                Generated an empty dataset for now."""
            )

    def EclFile_to_datapoint(self, ecl_file: EclFile) -> tuple[tf.Tensor, tf.Tensor]:
        """Extract values from an ``EclFile`` to form an (input, target) tuple of
        tensors.


        Parameters:
            ecl_file: _description_

        Raises:
            KeyError: If ``ecl_file`` does not have either of the keywords in
                ``self.input_kws`` or ``self.target_kws``

        Returns:
            A tuple containing the input and target tensor. The former has shape
            ``(ecl_file.num_report_steps(), num_cells, len(input_kws))``, while the
            latter has shape
            ``(ecl_file.num_report_steps(), num_cells, len(target_kws))``.

        """
        # Only add the datapoint if all input features and targets are
        # available.
        input: dict[str, np.ndarray] = {}
        target: dict[str, np.ndarray] = {}
        # The dic values are  ``np.ndarray`` of the property values
        # corresponding to the keyword, with shape
        # ``(ecl_file.num_report_steps(), num_cells)``.
        # TODO: Check that this is right!
        for input_kw in self.input_kws:
            if ecl_file.has_kw(input_kw):
                input[input_kw] = np.array(ecl_file.iget_kw(input_kw))
                # print(
                #     f"report step {0} input_kw {input_kw} shape {input[input_kw].shape}"
                # )
            else:
                raise KeyError(input_kw)
        for target_kw in self.target_kws:
            if ecl_file.has_kw(target_kw):
                target[target_kw] = np.array(ecl_file.iget_kw(target_kw))
            else:
                raise KeyError(target_kw)
        # Stack the different input and target properties into one input
        # and output tensor. ``len(input_kws)`` and ``len(target_kws)``
        # become the size of the last dimension.

        # MANUAL CHANGES: Change the lines below to change the shape of the input and
        # target tensors.
        return tf.stack(
            [tf.convert_to_tensor(val, dtype=self.dtype) for val in input.values()],
            axis=-1,
        ), tf.stack(
            [tf.convert_to_tensor(val, dtype=self.dtype) for val in target.values()],
            axis=-1,
        )

    def __len__(self):
        return self.inputs.shape[0]

    def __getitem__(self, idx) -> tuple[tf.Tensor, tf.Tensor]:
        x = self.inputs[idx]
        y = self.targets[idx]
        # TODO: Implement some functionality to make sure that x and y have the same
        # datatype.
        return x, y

    def __call__(self):
        for i in range(self.__len__()):
            yield self.__getitem__(i)

            # TODO: Fix ``on_epoch_end`` and reenable this call.
            if i == self.__len__() - 1 and self.shuffle_on_epoch_end:
                self.on_epoch_end()

    def on_epoch_end(self):
        """Shuffle the dataset at the end of each epoch.

        Warning:
            Using this method might give an error atm.

        """
        indices = tf.range(start=0, limit=self.inputs.shape[0], dtype=tf.int32)
        shuffled_indices = tf.random.shuffle(indices)
        self.inputs = tf.gather(self.inputs, shuffled_indices, axis=0)
        self.targets = tf.gather(self.targets, shuffled_indices, axis=0)


def main(args):
    """Create a dataset from the given arguments and store it"""
    data = EclDataSet(args.path, args.input_kws, args.target_kws, args.file_format)
    assert len(data) > 0
    ds = tf.data.Dataset.from_generator(
        data,
        output_signature=(
            tf.TensorSpec.from_tensor(data[0][0]),
            tf.TensorSpec.from_tensor(data[0][1]),
        ),
    )
    ds.save(args.save_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path", default=".", type=str, help="folder containing the *.UNRST files"
    )
    parser.add_argument(
        "--save-path",
        default="./ecl_dataset",
        type=str,
        help="save path for the tensorflow dataset",
    )
    parser.add_argument(
        "--input-kws",
        type=str,
        nargs="+",
        help="keywords to extract from the *.UNRST files for inputs of the dataset",
    )
    parser.add_argument(
        "--target-kws",
        type=str,
        nargs="+",
        help="keywords to extract from the *.UNRST files for targets of the dataset",
    )
    parser.add_argument(
        "--file-format",
        choices=["ecl", "opm"],
        type=str,
        help="type of the *.UNRST files (opm not implemented yet)",
    )
    args = parser.parse_args()
    main(args)
