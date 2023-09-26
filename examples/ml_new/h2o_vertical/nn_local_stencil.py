import os

import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from runspecs import runspecs_ensemble

from pyopmnearwell.ml import ensemble, nn
from pyopmnearwell.utils import formulas, units

dirname: str = os.path.dirname(__file__)

data_r_e_dirname: str = os.path.join(dirname, "dataset_r_e_pressure")
new_data_r_e_dirname: str = os.path.join(dirname, "dataset_r_e_pressure_local_stencil")
os.makedirs(new_data_r_e_dirname, exist_ok=True)

nn_r_e_dirname: str = os.path.join(dirname, "nn_r_e_pressure_local_stencil")
os.makedirs(nn_r_e_dirname, exist_ok=True)

# Load the dataset and restructure the features.
ds: tf.data.Dataset = tf.data.Dataset.load(data_r_e_dirname)
features, targets = next(iter(ds.batch(batch_size=len(ds)).as_numpy_iterator()))

# At the upper and lower boundary the neighbor values are padded with zeros. Note that
# the arrays go from upper to lower cells.
new_features: list[np.ndarray] = []
for i in range(features.shape[-1] - 1):
    feature = features[..., i]
    # The features have ``ndim == 3``: ``(npoints, num_timesteps, num_layers)``. The
    # last dimension is padded.
    feature_upper = np.pad(
        feature[..., :-1],
        ((0, 0), (0, 0), (1, 0)),
        mode="constant",
        constant_values=0,
    )
    feature_lower = np.pad(
        feature[..., 1:],
        ((0, 0), (0, 0), (0, 1)),
        mode="constant",
        constant_values=0,
    )
    new_features.extend([feature_upper, feature, feature_lower])

# Add time back again.
new_features.append(features[..., -1])
new_features_array: np.ndarray = np.stack(new_features, axis=-1)

# The new features are in the following order:
# 1. PRESSURE - upper neighbor
# 2. PRESSURE - cell
# 3. PRESSURE - lower neighbor
# 4. TIME

ensemble.store_dataset(
    new_features_array.reshape(-1, new_features_array.shape[-1]),
    targets.flatten()[..., None],
    new_data_r_e_dirname,
)

# Train model
model = nn.get_FCNN(ninputs=4, noutputs=1)
train_data, val_data = nn.scale_and_prepare_dataset(
    new_data_r_e_dirname,
    feature_names=[
        "pressure_upper",
        "pressure",
        "pressure_lower",
        "time",
    ],
    savepath=nn_r_e_dirname,
)
nn.train(
    model,
    train_data,
    val_data,
    savepath=nn_r_e_dirname,
    epochs=100,
)


# Plot bhp for the first layer
timesteps: np.ndarray = np.arange(4)  # No unit.

for features_member, targets_member, i in list(
    zip(
        new_features_array[:: features.shape[0], ..., 0, :],
        targets[:: features.shape[0], ..., 0, 0],
        range(features[:: features.shape[0], ...].shape[0]),
    )
):
    # Cell pressure is given by the second feature
    pressures_member: np.ndarray = features_member[..., 1]

    # Loop through all time steps and collect analytical WIs.
    WI_analytical = []
    for pressure in pressures_member:
        # Evaluate density and viscosity.
        density = formulas.co2brinepvt(
            pressure=pressure,
            temperature=runspecs_ensemble["constants"]["INIT_TEMPERATURE"]
            + units.CELSIUS_TO_KELVIN,
            property="density",
            phase="water",
        )

        viscosity = formulas.co2brinepvt(
            pressure=pressure,
            temperature=runspecs_ensemble["constants"]["INIT_TEMPERATURE"]
            + units.CELSIUS_TO_KELVIN,
            property="viscosity",
            phase="water",
        )

        # Calculate the well index from Peaceman. The analytical well index is in [m*s],
        # hence we need to devide by surface density to transform to [m^4*s/kg].
        WI_analytical.append(
            formulas.peaceman_WI(
                k_h=runspecs_ensemble["constants"]["PERMX"]
                * units.MILIDARCY_TO_M2
                * runspecs_ensemble["constants"]["HEIGHT"]
                / runspecs_ensemble["constants"]["NUM_ZCELLS"],
                r_e=formulas.equivalent_well_block_radius(200),
                r_w=0.25,
                rho=density,
                mu=viscosity,
            )
            / runspecs_ensemble["constants"]["SURFACE_DENSITY"]
        )

    injection_rate: float = runspecs_ensemble["constants"]["INJECTION_RATE_PER_SECOND"]
    WI_nn: np.ndarray = nn.scale_and_evaluate(
        model, features_member, os.path.join(nn_r_e_dirname, "scalings.csv")
    )[..., 0]

    # We need to divide by num_zcells, as the injection rate is given for the
    # entire length of the well. To get the injection rate in one cells we assume the
    # injection rate is constant along the well.
    injection_rate_per_second_per_cell: float = (
        injection_rate / runspecs_ensemble["constants"]["NUM_ZCELLS"]
    )
    bhp_nn: np.ndarray = injection_rate_per_second_per_cell / WI_nn + pressure
    bhp_data: np.ndarray = (
        injection_rate_per_second_per_cell / targets_member + pressure
    )
    bhp_analytical: np.ndarray = (
        injection_rate_per_second_per_cell / np.array(WI_analytical) + pressure
    )
    plt.figure()
    plt.scatter(
        timesteps * 3 + 1,
        bhp_data,
        label="data",
    )
    plt.plot(
        timesteps * 3 + 1,
        bhp_nn,
        label="NN",
    )
    plt.plot(
        timesteps * 3 + 1,
        bhp_analytical,
        label="Peaceman",
    )
    plt.legend()
    plt.xlabel(r"$t\,[d]$")
    plt.ylabel(r"$p\,[Pa]$")
    plt.savefig(
        os.path.join(
            dirname,
            nn_r_e_dirname,
            f"p_data_vs_nn_vs_Peaceman_{i}.png",
        )
    )
    plt.show()
