import math
import os
import pathlib
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

from pyopmnearwell.ml import ensemble
from pyopmnearwell.utils import formulas, units


class BaseDataset:
    """Provide methods to create a dataset from ensemble dataset.

    This base class provides several methods to obtain features from a dataset and reduce
    dimensions. This is done by averaging/summing/etc. values along all vertical cells
    inside layer and by taking only some timesteps/horizontal cells.

    Subclasses need to implement ``__init__`` and (if needed) ``create_ds`` methods.

    The feature array will have shape ``(num_ensemble_runs, num_timesteps/step_size_t,
    num_layers, num_xcells/step_size_x, num_features)``.
    The target array will have shape ``(num_ensemble_runs, num_timesteps/step_size_t,
    num_layers, num_xcells/step_size_x, 1)``

    Note: All methods assume that all cells have the same height. if this is not the
        case, the methods must be overridden.

    """

    num_timesteps: int
    num_layers: int
    num_zcells: int
    num_xcells: int
    single_feature_shape: tuple

    def __init__(self):
        pass

    def create_ds(self):
        pass

    def reduce_data_size(
        self, feature: np.ndarray, step_size_x: int = 1, step_size_t: int = 1
    ) -> np.ndarray:
        return feature[:, ::step_size_t, ::, ::step_size_x]

    def get_vertically_averaged_values(
        self, features: np.ndarray, feature_index
    ) -> np.ndarray:
        """Average features vertically inside each layer.

        Args:
            features (np.ndarray): _description_
            feature_index (int): _description_.

        Returns:
            np.ndarray (``shape = (num_ensemble_runs, num_timesteps, num_layers,
                num_xcells)``):

        """
        feature: np.ndarray = np.average(features[..., feature_index], axis=-2)[..., 1:]
        assert feature.shape == self.single_feature_shape
        return feature

    def get_radii(self, radii_file: pathlib.Path) -> tuple[np.ndarray, np.ndarray]:
        """Get full list of cell radii."""
        cell_center_radii, inner_radii, outer_radii = ensemble.calculate_radii(
            radii_file,
            num_cells=40,
            return_outer_inner=True,
            triangle_grid=True,
            theta=math.pi / 3,  # TODO: More flexible
        )
        cell_boundary_radii: np.ndarray = np.append(inner_radii, outer_radii[-1])
        assert cell_center_radii.shape == self.num_xcells
        assert cell_boundary_radii.shape == self.num_xcells + 1
        return cell_center_radii, cell_boundary_radii

    def get_timesteps(self, simulation_length: float) -> np.ndarray:
        """_summary_

        Returns:
            np.ndarray (``shape = (num_timesteps,) ``): Unit: [d].

        """
        timesteps: np.ndarray = np.linspace(0, simulation_length, self.num_timesteps)
        assert timesteps.shape == self.num_timesteps
        return timesteps

    def get_horizontically_integrated_values(
        self,
        features: np.ndarray,
        cell_center_radii: np.ndarray,
        cell_boundary_radii: np.ndarray,
        feature_index: int,
    ):
        """Integrate feature horizontically along layers and divide by equivalent
        cartesian block area.

        Note:
            - Before integrating, the feature is averaged vertically inside each layer.
            - The integration takes place in 2D, hence it suffices to divide by area and
            not by  volume.

        Args:
            features (np.ndarray): _description_
            cell_center_radii (np.ndarray):
            cell_boundary_radii (np.ndarray):
            feature_index (int): _description_. Default is 1.

        Returns:
            np.ndarray (``shape = (num_ensemble_runs, num_timesteps, num_layers,
                num_xcells)``): Features values average for each cell.

        """
        # Average along vertical cells in a layer.
        feature: np.ndarray = np.average(features[..., feature_index], axis=-2)
        # Integrate horizontically along layers and divide by equivalent cartesian block
        # area.
        block_sidelengths: np.ndarray = formulas.cell_size(cell_center_radi)
        feature = ensemble.integrate_fine_scale_value(
            feature,
            cell_boundary_radii,
            block_sidelengths,
        ) / (block_sidelengths**2)
        assert feature.shape == self.single_feature_shape
        return feature

    def get_homogeneous_values(self, features, feature_index):
        """Get a feature that is homogeneous inside a layer.

        Note: Since the feature is equal inside a layer, this method takes the first
        value for each layer.

        Args:
            features (np.ndarray): _description_
            feature_index (int): _description_.

        Returns:
            np.ndarray (``shape = (num_ensemble_runs, num_timesteps, num_layers,
                num_xcells)``):

        """
        feature: np.ndarray = features[..., feature_index][..., 0, :]
        assert feature.shape == self.single_feature_shape
        return feature

    def get_analytical_WI(
        self,
        pressures: np.ndarray,
        saturations: np.ndarray,
        permeabilities: np.ndarray,
        temperature: float,
        radii: np.ndarray,
        OPM: pathlib.Path,
    ) -> np.ndarray:
        densities_lst: list[list[float]] = []
        viscosities_lst: list[list[float]] = []
        for pressure in pressures.flatten():
            # Evaluate density and viscosity.
            density_tuple: list[float] = []
            viscosity_tuple: list[float] = []

            for phase in ["water", "CO2"]:
                density_tuple.append(
                    formulas.co2brinepvt(
                        pressure=pressure,
                        temperature=temperature + units.CELSIUS_TO_KELVIN,
                        phase_property="density",
                        phase=phase,
                        OPM=OPM,
                    )
                )

                viscosity_tuple.append(
                    formulas.co2brinepvt(
                        pressure=pressure,
                        temperature=temperature + units.CELSIUS_TO_KELVIN,
                        phase_property="viscosity",
                        phase=phase,
                        OPM=OPM,
                    )
                )
            densities_lst.append(density_tuple)
            viscosities_lst.append(viscosity_tuple)

        densities_shape = list(pressures.shape)
        densities_shape.extend([2])
        densities: np.ndarray = np.array(densities_lst).reshape(densities_shape)
        viscosities: np.ndarray = np.array(viscosities_lst).reshape(densities_shape)

        # Calculate the well index from Peaceman. The analytical well index is in [m*s],
        # hence we need to devide by surface density to transform to [m^4*s/kg].
        analytical_WI: np.ndarray = (
            formulas.two_phase_peaceman_WI(
                k_h=permeabilities
                * units.MILIDARCY_TO_M2
                * (self.num_zcells / self.num_layers),
                r_e=radii,
                r_w=0.25,
                rho_1=densities[..., 0],
                mu_1=viscosities[..., 0],
                k_r1=(1 - saturations) ** 2,
                rho_2=densities[..., 1],
                mu_2=viscosities[..., 1],
                k_r2=saturations**2,
            )
            / runspecs_ensemble["constants"]["SURFACE_DENSITY"]
        )

        assert analytical_WI.shape == self.single_feature_shape
        return analytical_WI

    def get_data_WI(
        self,
        features: np.ndarray,
        pressures: np.ndarray,
        pressure_index: int = 0,
        inj_rate_index: int = 3,
    ) -> np.ndarray:
        # Take the pressure values of the well blocks as bhp.
        bhps: np.ndarray = np.average(features[..., pressure_index], axis=-2)[
            ..., 0
        ]  # ``shape = (num_completed_runs, num_timesteps/3, num_layers); unit [bar]

        # Get the individual injection rates per second for each cell. Multiply by 6 to account
        # for the 60° cake and transform to rate per second.
        injection_rate_per_second_per_cell: np.ndarray = (
            np.average(features[..., inj_rate_index], axis=-2)[..., 0]
            * 6
            * units.Q_per_day_to_Q_per_seconds
        )  # ``shape = (num_completed_runs, num_timesteps/3, num_layers)
        # Check that we do not divide by zero.
        assert np.all(bhps - pressures)
        WI_data: np.ndarray = injection_rate_per_second_per_cell / (bhps - pressures)
        assert WI_data.shape == self.single_feature_shape
        return WI_data
