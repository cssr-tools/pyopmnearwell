import os

import numpy as np
import tensorflow as tf
from matplotlib import pyplot as plt
from runspecs import runspecs_ensemble_3 as runspecs_ensemble
from runspecs import trainspecs_13 as trainspecs

from pyopmnearwell.ml import ensemble, nn
from pyopmnearwell.utils import formulas, units

FEATURE_TO_INDEX: dict[str, int] = {
    "pressure_upper": 0,
    "pressure": 1,
    "pressure_lower": 2,
    "permeability_upper": 3,
    "permeability": 4,
    "permeability_lower": 5,
    "time": 6,
}


# Create dirs
dirname: str = os.path.dirname(__file__)

data_dirname: str = os.path.join(dirname, f"dataset_{runspecs_ensemble['name']}")
new_data_dirname: str = os.path.join(
    dirname, f"dataset_{runspecs_ensemble['name']}_{trainspecs['name']}"
)
os.makedirs(new_data_dirname, exist_ok=True)

nn_dirname: str = os.path.join(
    dirname, f"nn_{runspecs_ensemble['name']}_{trainspecs['name']}"
)
os.makedirs(nn_dirname, exist_ok=True)

# Restructure data:
ds: tf.data.Dataset = tf.data.Dataset.load(data_dirname)
features, targets = next(iter(ds.batch(batch_size=len(ds)).as_numpy_iterator()))

# Pad values at the upper and lower boundary.
# NOTE: The arrays range FROM upper TO lower cells.
new_features: list[np.ndarray] = []
for i in range(features.shape[-1] - 1):
    feature: np.ndarray = features[..., i]

    # Pressure options:
    if i == 0:
        if trainspecs["pressure_unit"] == "bar":
            feature = feature * units.PASCAL_TO_BAR

        if trainspecs["pressure_padding"] == "zeros":
            padding_mode: str = "constant"
            padding_value: float = 0.0

        # TODO: Fix init padding mode. Where to get the pressure value from? The
        # runspecs only have the ensemble values. The data truncates the init value.
        # elif trainspecs["pressure_padding"] == "init":
        #     padding_mode = "constant"
        #     padding_values  = runspecs_ensemble["constant"]

        elif trainspecs["pressure_padding"] == "neighbor":
            padding_mode = "edge"
            padding_value = 0.0

    # Permeability options:
    elif i == 1:
        if trainspecs["permeability_log"]:
            feature = np.log10(feature)

        if trainspecs["permeability_padding"] == "zeros":
            padding_mode = "constant"
            padding_value = 0.0

    # The features have ``ndim == 3``: ``(npoints, num_timesteps, num_layers)``. The
    # last dimension is padded.
    # Ignore MypY complaining.
    if padding_mode == "constant":
        feature_upper = np.pad(  # type: ignore
            feature[..., :-1],
            ((0, 0), (0, 0), (1, 0)),
            mode=padding_mode,
            constant_values=padding_value,
        )
        feature_lower = np.pad(  # type: ignore
            feature[..., 1:],
            ((0, 0), (0, 0), (0, 1)),
            mode=padding_mode,
            constant_values=padding_value,
        )
    else:
        feature_upper = np.pad(  # type: ignore
            feature[..., :-1],
            ((0, 0), (0, 0), (1, 0)),
            mode=padding_mode,
        )
        feature_lower = np.pad(  # type: ignore
            feature[..., 1:],
            ((0, 0), (0, 0), (0, 1)),
            mode=padding_mode,
        )

    new_features.extend([feature_upper, feature, feature_lower])

# Time was not padded and is added back again.
new_features.append(features[..., -1])
new_features_array: np.ndarray = np.stack(new_features, axis=-1)

# Select the correct features from the train specs
new_features_final: np.ndarray = new_features_array[
    ..., [FEATURE_TO_INDEX[feature] for feature in trainspecs["features"]]
]

if trainspecs["WI_log"]:
    targets = np.log10(targets)

# The new features are in the following order:
# 1. PRESSURE - upper neighbor
# 2. PRESSURE - cell
# 3. PRESSURE - lower neighbor
# 4. PERMEABILITY - upper neighbor
# 5. PERMEABILITY - cell
# 6. PERMEABILITY - lower neighbor
# 7. TIME

ensemble.store_dataset(
    new_features_final.reshape(-1, new_features_final.shape[-1]),
    targets.flatten()[..., None],
    new_data_dirname,
)


# Train model:
model = nn.get_FCNN(
    ninputs=len(trainspecs["features"]),
    noutputs=1,
    depth=trainspecs["depth"],
    hidden_dim=trainspecs["hidden_dim"],
    activation=trainspecs.get("activation", "sigmoid"),
    kernel_initializer="glorot_uniform",
    normalization=trainspecs["Z-normalization"],
)
train_data, val_data = nn.scale_and_prepare_dataset(
    new_data_dirname,
    feature_names=trainspecs["features"],
    savepath=nn_dirname,
    scale=trainspecs["MinMax_scaling"],
)

# Adapt the layers when using z-normalization.
if trainspecs["Z-normalization"]:
    model.layers[0].adapt(train_data[0])
    model.layers[-1].adapt(train_data[1])

kerasify = not trainspecs["Z-normalization"]
nn.train(
    model,
    train_data,
    val_data,
    savepath=nn_dirname,
    epochs=trainspecs["epochs"],
    loss_func=trainspecs["loss"],
    kerasify=kerasify,
)

# Comparison nn WI vs. Peaceman WI vs. data WI for 3 layers for the first ensemble
# member.
timesteps: np.ndarray = np.linspace(0, 1, features.shape[-3]) / 1  # unit: [day]

for i in [0, 3, 5, 7, 9]:
    features_member: np.ndarray = new_features_final[0, ..., i, :]

    # Cell pressure is given by the second feature, cell permeability by the fifth.
    pressures_member: np.ndarray = new_features_array[0, ..., i, 1]
    permeabilities_member: np.ndarray = new_features_array[0, ..., i, 4]
    WI_data: np.ndarray = targets[0, ..., i, 0]

    # Rescale to values used by OPM etc.
    if trainspecs["pressure_unit"] == "bar":
        pressures_member * units.PASCAL_TO_BAR
    if trainspecs["permeability_log"]:
        permeabilities_member = 10**permeabilities_member
    # Rescale if the targets were scaled.
    if trainspecs["WI_log"]:
        WI_data = 10**WI_data

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

    WI_nn: np.ndarray = nn.scale_and_evaluate(
        model, features_member, os.path.join(nn_dirname, "scalings.csv")
    )[..., 0]
    # Rescale if the targets were scaled.
    if trainspecs["WI_log"]:
        WI_nn = 10**WI_nn

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
    plt.title(f"Layer {i} permeability {permeabilities_member[0]:.2f} [mD]")
    plt.savefig(
        os.path.join(
            dirname,
            nn_dirname,
            f"WI_data_vs_nn_vs_Peaceman_{i}.png",
        )
    )
    plt.show()
