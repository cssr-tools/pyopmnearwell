import os
import pathlib

from pyopmnearwell.ml import integration

dirname: pathlib.Path = pathlib.Path(__file__).parent
OPM_ML: pathlib.Path = "/home/peter/Documents/2023_CEMRACS/opm_ml"
FLOW_ML: str = f"{OPM_ML}/build/opm-simulators/bin/flow_gaswater_dissolution_diffuse"

integration.recompile_flow(
    dirname / "scalings.csv",
    "local_stencil",
    OPM_ML,
    standard_well_file="local_stencil",
    stencil_size=3,
    local_feature_names=["pressure"],
)
