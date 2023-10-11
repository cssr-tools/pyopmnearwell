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
    feature: np.ndarray = features[..., i]

    # Scale to bar for pressures
    if i == 0:
        feature = feature * units.PASCAL_TO_BAR
    # Take log for permeabilities
    elif i == 1:
        feature = np.log10(feature)

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
# 4. PERMEABILITY - upper neighbor
# 5. PERMEABILITY - cell
# 6. PERMEABILITY - lower neighbor
# 7. TIME

ensemble.store_dataset(
    new_features_array.reshape(-1, new_features_array.shape[-1]),
    targets.flatten()[..., None],
    new_data_r_e_dirname,
)

# Train model
model = nn.get_FCNN(
    ninputs=7, noutputs=1, depth=3, hidden_dim=10, kernel_initializer="glorot_uniform"
)
train_data, val_data = nn.scale_and_prepare_dataset(
    new_data_r_e_dirname,
    feature_names=[
        "pressure_upper",
        "pressure",
        "pressure_lower",
        "permeability_upper",
        "permeability",
        "permeability_lower",
        "time",
    ],
    savepath=nn_r_e_dirname,
)
nn.train(
    model,
    train_data,
    val_data,
    savepath=nn_r_e_dirname,
    epochs=1000,
)

# Comparison nn WI vs. Peaceman WI vs. data WI for 3 layers for the first ensemble
# member.
timesteps: np.ndarray = np.linspace(0, 1, features.shape[-3]) / 1  # unit: [day]

for i in [0, 3, 5, 7, 9]:
    # Cell pressure is given by the second feature, cell permeability by the fifth.
    # Rescale to values used by OPM etc.
    features_member: np.ndarray = new_features_array[0, ..., i, :]
    pressures_member: np.ndarray = (
        new_features_array[0, ..., i, 1] * units.BAR_TO_PASCAL
    )
    permeabilities_member: np.ndarray = 10 ** new_features_array[0, ..., i, 4]

    #
    WI_data = targets[0, ..., i, 0]

    # Loop through all time steps and collect analytical WIs.
    WI_analytical = []
    for pressure, permeability in zip(pressures_member, permeabilities_member):
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
                k_h=permeability
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

    plt.figure()
    plt.scatter(
        timesteps,
        WI_data,
        label="data",
    )
    plt.plot(
        timesteps,
        WI_nn,
        label="NN",
    )
    plt.plot(
        timesteps,
        WI_analytical,
        label="Peaceman",
    )
    plt.legend()
    plt.xlabel(r"$t\,[d]$")
    plt.ylabel(r"$WI\,[m^4\cdot s/kg]$")
    plt.title(f"Layer {i}")
    plt.savefig(
        os.path.join(
            dirname,
            nn_r_e_dirname,
            f"WI_data_vs_nn_vs_Peaceman_{i}.png",
        )
    )
    plt.show()
