# pylint: disable=fixme,missing-function-docstring,no-member, pointless-string-statement
"""Functionality to upscale data from an ensemble run on a radial grid to a cartesian
grid.

Note: pylint: no-member is disabled, because it complains about the ``BaseUpscaler``
missing instance attributes, which are taken care of by the ``Upscaler`` protocol.
pylint: pointless-string-statement is disabled, as it complains an attribute docstring
in the ``Upscaler`` protocol.

"""

import math
import pathlib
from abc import ABC, abstractmethod
from typing import Protocol

import numpy as np

# ``tqdm`` is not a dependency. Up to the user to install it.
try:
    # Avoid some mypy trouble.
    import tqdm.autonotebook as tqdm  # type: ignore
except ImportError:
    _IS_TQDM_AVAILABLE: bool = False
else:
    _IS_TQDM_AVAILABLE = True

from pyopmnearwell.ml import ensemble
from pyopmnearwell.utils import formulas, units


class Upscaler(Protocol):
    """Protocol class for upscalers.

    This class is used for typing of abstract attributes of ``BaseUpscaler``. MyPy will
    check if subclasses of ``BaseUpscaler`` implement the following instance attributes:

    - ``num_timesteps``
    - ``num_layers``
    - ``num_zcells``
    - ``num_xcells``
    - ``single_feature_shape``

    However, in comparison to missing abstract functions, no runtime error will be
    raised if they are missing.

    See, e.g., https://stackoverflow.com/a/75253719 for an explanation.

    Note: As of now (Python 3.11), each instance method of ``BaseUpscaler`` or a
        subclass making use of one of the attributes, needs to have its self argumented
        annotated with ``Upscaler``. In future python versions it should be possible to
        use ``class BaseUpscaler[Upscaler](ABC):...`` instead and remove these
        annotations.

    """

    @property
    def num_timesteps(self) -> int: ...

    @property
    def num_layers(self) -> int: ...

    @property
    def num_zcells(self) -> int: ...

    @property
    def num_xcells(self) -> int: ...

    @property
    def single_feature_shape(self) -> tuple: ...

    @property
    def angle(self) -> float: ...

    """Angle of the cake radial grid. Default is 60°."""


class BaseUpscaler(ABC):
    """Extract and upscale data from an array of ensemble data.

    This base class provides several methods to extract features from fine-scale radial
    simulations and upscale to coarse cartesian cells. Depending on the type of data,
    this is done by averaging/summing/etc. values along all cells that correspond to a
    coarse cell.

    Additionally, the sparsity of the dataset can be increased by taking only some
    timesteps/horizontal cells.

    The upscaled data is usually provided in form of two ``np.ndarrays``, one for
    features and one for targets.

    Subclasses need to implement ``__init__`` and (if needed) ``create_ds`` methods.

    The feature array will have shape ``(num_ensemble_runs, num_timesteps/step_size_t,
    num_layers, num_xcells/step_size_x, num_features)``.
    The target array will have shape ``(num_ensemble_runs, num_timesteps/step_size_t,
    num_layers, num_xcells/step_size_x, 1)``

    Note: All methods assume that all cells have the same height. if this is not the
        case, the methods must be overridden.

    """

    @abstractmethod
    def __init__(self: Upscaler):  # pylint: disable=missing-function-docstring
        return

    @abstractmethod
    def create_ds(self: Upscaler):  # pylint: disable=missing-function-docstring
        return

    def reduce_data_size(
        self: Upscaler,
        feature: np.ndarray,
        step_size_x: int = 1,
        step_size_t: int = 1,
        random: bool = False,
    ) -> np.ndarray:
        """Reduce the size of the input feature array by selecting elements with a
        fixed step size.

        Args:
            feature (np.ndarray): The input feature array.
            step_size_x (int, optional): The step size for the x-axis. Defaults to 1.
            step_size_t (int, optional): The step size for the t-axis. Defaults to 1.
            random (bool, optional): If True, select elements randomly instead of using
                a fixed step size. Defaults to False. Not implemented yet.

        Returns:
            np.ndarray: The reduced feature array.

        """
        # TODO: Add option to have a random selection of elements for each member,
        # instead of a fixed stepsize. This needs to be the same for each feature, hence
        # the current idea does not work.
        if random:
            pass
        return feature[:, ::step_size_t, ::, ::step_size_x]

    def get_vertically_averaged_values(
        self: Upscaler,
        features: np.ndarray,
        feature_index,
        disregard_first_xcell: bool = True,
    ) -> np.ndarray:
        """Average features vertically inside each layer.

        Args:
            features (np.ndarray): _description_
            feature_index (int): _description_.
            disregard_first_xcell (bool): __description__. Default is True.

        Returns:
            np.ndarray:
                ``shape = (num_ensemble_runs, num_timesteps, num_layers, num_xcells)``

        """
        # Innermost cells (well cells) get disregarded.
        feature: np.ndarray = np.average(features[..., feature_index], axis=-2)

        if disregard_first_xcell:
            feature = feature[..., 1:]
            assert feature.shape == self.single_feature_shape

        else:
            assert feature.shape[:-1] == self.single_feature_shape[:-1]
            assert feature.shape[-1] == self.single_feature_shape[-1] + 1

        return feature

    def get_radii(
        self: Upscaler, radii_file: pathlib.Path
    ) -> tuple[np.ndarray, np.ndarray]:
        """Get full list of cell radii."""
        cell_center_radii, inner_radii, outer_radii = ensemble.calculate_radii(
            radii_file,
            num_cells=self.num_xcells + 1,
            return_outer_inner=True,
            triangle_grid=True,
            angle=self.angle,
        )
        # Innermost cells (well cells) get disregarded. If the cell_boundary_radii are
        # used for integrating, this is actually needed, as the content of the well does
        # not count towards the well block, hence the well radius should not be
        # integrated.
        cell_center_radii = cell_center_radii[1:]
        inner_radii = inner_radii[1:]
        outer_radii = outer_radii[1:]

        cell_boundary_radii: np.ndarray = np.append(inner_radii, outer_radii[-1])
        assert cell_center_radii.shape == (self.num_xcells,)
        assert cell_boundary_radii.shape == (self.num_xcells + 1,)
        return cell_center_radii, cell_boundary_radii

    def get_timesteps(self: Upscaler, simulation_length: float) -> np.ndarray:
        """_summary_

        Returns:
            np.ndarray: Array with ``shape = (num_timesteps,) and Unit [d]``.
        """
        timesteps: np.ndarray = np.linspace(0, simulation_length, self.num_timesteps)
        assert timesteps.shape == self.num_timesteps
        return timesteps

    def get_horizontically_integrated_values(  # pylint: disable=too-many-positional-arguments, too-many-arguments
        self: Upscaler,
        features: np.ndarray,
        cell_center_radii: np.ndarray,
        cell_boundary_radii: np.ndarray,
        feature_index: int,
        disregard_first_xcell: bool = True,
    ):
        """Integrate feature horizontically along layers and divide by equivalent
        cartesian block area.

        Note:

            - Before integrating, the feature is averaged vertically inside each layer.
            - As the feature is averaged and not summed, the integration takes place in
              2D with vertically averaged values. Hence it suffices to divide by area
              and not by  volume.

        Args:
            features (np.ndarray): _description_
            cell_center_radii (np.ndarray):
            cell_boundary_radii (np.ndarray):
            feature_index (int): _description_. Default is 1.
            disregard_first_xcell (bool): __description__. Default is True.

        Returns:
            np.ndarray (``shape = (num_ensemble_runs, num_timesteps, num_layers, num_xcells)``):
                Features values average for each cell.

        """
        # Average along vertical cells in a layer.
        feature: np.ndarray = np.average(features[..., feature_index], axis=-2)

        if disregard_first_xcell:
            feature = feature[..., 1:]

        # Integrate horizontically along layers and divide by equivalent cartesian block
        # area.
        block_sidelengths: np.ndarray = formulas.cell_size(cell_center_radii)  # type: ignore
        # feature_lst: list[np.ndarray] = []
        # for i in range(feature.shape[-1]):
        #     feature_lst.append(
        #         ensemble.integrate_fine_scale_value(
        #             feature[..., : i + 1],
        #             cell_boundary_radii[: i + 2],
        #             block_sidelengths[: i + 1],
        #         )
        #         / (block_sidelengths[i] ** 2)
        #     )
        # averaged_feature: np.ndarray = np.concatenate(feature_lst, axis=-1)
        # The horizontal dimension is the last axis of each feature, hence we pass
        # ``axis=-1``.
        integrated_feature: np.ndarray = ensemble.integrate_fine_scale_value(
            feature, cell_boundary_radii, block_sidelengths, axis=-1
        ) / (block_sidelengths**2)

        assert integrated_feature.shape == self.single_feature_shape
        return integrated_feature

    def get_homogeneous_values(
        self: Upscaler, features, feature_index, disregard_first_xcell: bool = True
    ):
        """Get a feature that is homogeneous inside a layer.

        Note: Since the feature is equal inside a layer, this method takes the first
        value for each layer.

        Args:
            features (np.ndarray): _description_
            feature_index (int): _description_.
            disregard_first_xcell (bool): __description__. Default is True.

        Returns:
            np.ndarray (``shape = (num_ensemble_runs, num_timesteps, num_layers, num_xcells)``)

        """
        # Innermost cells (well cells) get disregarded.
        feature: np.ndarray = features[..., feature_index][..., 0, :]

        if disregard_first_xcell:
            feature = feature[..., 1:]

        assert feature.shape == self.single_feature_shape
        return feature

    def get_analytical_PI(  # pylint: disable=invalid-name
        self: Upscaler,
        permeabilities: np.ndarray,
        cell_heights: np.ndarray,
        radii: np.ndarray,
        well_radius: float,
    ) -> np.ndarray:
        """_summary_

        _extended_summary_

        Args:
            permeabilities (np.ndarray): Unit has to be [m^2]!
            cell_heights (np.ndarray): Unit [m].
            radii (np.ndarray): _description_
            well_radius (float): _description_

        Returns:
            np.ndarray: _description_
        """
        analytical_PI: np.ndarray = formulas.peaceman_matrix_WI(  # type: ignore
            k_h=permeabilities * cell_heights,
            r_e=radii,
            r_w=well_radius,
        )
        assert analytical_PI.shape == self.single_feature_shape
        return analytical_PI

    # pylint: disable-next=invalid-name, too-many-positional-arguments, too-many-locals, too-many-arguments
    def get_analytical_WI(
        self: Upscaler,
        pressures: np.ndarray,
        saturations: np.ndarray,
        permeabilities: np.ndarray,
        temperature: float,
        surface_density: float,
        radii: np.ndarray,
        well_radius: float,
        # pylint: disable-next=invalid-name
        OPM: pathlib.Path,
    ) -> np.ndarray:
        """_summary_

        _extended_summary_

        Args:
            pressures (np.ndarray): _description_
            saturations (np.ndarray): _description_
            permeabilities (np.ndarray): Unit has to be [mD]!
            temperature (float): _description_
            surface_density (float): _description_
            radii (np.ndarray): _description_
            well_radius (float): _description_
            OPM (pathlib.Path): _description_

        Returns:
            np.ndarray: _description_

        """
        densities_lst: list[list[float]] = []
        viscosities_lst: list[list[float]] = []
        # ``formulas.co2brinepvt`` calls CO2BRINEPVT from OPM Flow for each pressure,
        # which is quite inefficient. If tqdm is available, we show a progress bar.
        if _IS_TQDM_AVAILABLE:
            pressures_bar = tqdm.tqdm(pressures.flatten())
        else:
            pressures_bar = pressures.flatten()

        for pressure in pressures_bar:
            # Evaluate density and viscosity.
            density_tuple: list[float] = []
            viscosity_tuple: list[float] = []

            for phase in ["water", "CO2"]:
                density_tuple.append(
                    formulas.co2brinepvt(
                        pressure=pressure,
                        temperature=temperature + units.CELSIUS_TO_KELVIN,
                        phase_property="density",
                        phase=phase,  # type: ignore
                        OPM=OPM,
                    )
                )

                viscosity_tuple.append(
                    formulas.co2brinepvt(
                        pressure=pressure,
                        temperature=temperature + units.CELSIUS_TO_KELVIN,
                        phase_property="viscosity",
                        phase=phase,  # type: ignore
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
        # pylint: disable-next=invalid-name
        analytical_WI: np.ndarray = (  # type: ignore
            # Ignore unsupported operand types for *. Fixing this would be quite
            # complex.
            formulas.two_phase_peaceman_WI(  # type: ignore
                k_h=permeabilities
                * units.MILIDARCY_TO_M2
                * (
                    self.num_zcells / self.num_layers
                ),  # TODO: This is FALSE, it must be height instead!
                r_e=radii,
                r_w=well_radius,
                rho_1=densities[..., 0],
                mu_1=viscosities[..., 0],
                k_r1=(1 - saturations) ** 2,
                rho_2=densities[..., 1],
                mu_2=viscosities[..., 1],
                k_r2=saturations**2,
            )
            / surface_density
        )

        # TODO: Add this assert again. It's turned off s.t. the analytical WI can be
        # computed after size reduction of features.
        # assert analytical_WI.shape == self.single_feature_shape
        return analytical_WI

    def get_data_WI(  # pylint: disable=invalid-name
        self: Upscaler,
        features: np.ndarray,
        pressure_index: int,
        inj_rate_index: int,
        angle: float = math.pi / 3,
    ) -> np.ndarray:
        """Calculate data-driven WI from pressure and flow rate.

        Similar functionality to ``ensemble.calculate_WI``, but can additionally treat
        multiple vertical cells in a layer correctly.

        Note:
            - Pressures get averaged over each layer, injection rates get summed over
              each layer.
            - The method automatically scales the near-well injection rate from the cake
              grid with angle ``angle`` to a 360° well. Furthermore, the rate is scaled
              from rate-per-day (which the results are in) to rate-per-second, which OPM
              Flow uses internally for the WI.


        Args:
            features (np.ndarray): _description_
            pressure_index (int): _description_
            inj_rate_index (int): _description_

        Returns:
            np.ndarray: _description_

        """
        # Take the pressure values of the well blocks as bhp. Average along each layer.
        bhps: np.ndarray = np.average(features[..., pressure_index], axis=-2)[..., 0][
            ..., None
        ]  # ``shape = (num_completed_runs, num_timesteps, num_layers, 1)``

        # Ge the pressure values of all other blocks. Average along each layer.
        pressures: np.ndarray = np.average(features[..., pressure_index], axis=-2)[
            ..., 1:
        ]  # ``shape = (num_completed_runs, num_timesteps, num_layers, num_xcells)``

        # Get the individual injection rates per second for each layer. Sum across a
        # layer to get the rates for a full layer. Multiply by
        # ``(math.pi * 2 / angle)`` to transform from a cake of given ``angle`` to a
        # full radial model and convert to rate per second.
        injection_rate_per_second_per_cell: np.ndarray = (
            np.sum(features[..., inj_rate_index], axis=-2)[..., 0]
            * (math.pi * 2 / angle)
            * units.Q_per_day_to_Q_per_seconds
        )[
            ..., None
        ]  # ``shape = (num_completed_runs, num_timesteps, num_layers, 1)``

        # Check that we do not divide by zero.
        assert np.all(bhps - pressures)
        WI_data: np.ndarray = injection_rate_per_second_per_cell / (bhps - pressures)
        assert WI_data.shape == self.single_feature_shape
        return WI_data
