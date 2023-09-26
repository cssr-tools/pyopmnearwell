import os

from runspecs import runspecs_integration

from pyopmnearwell.ml import integration

dirname: str = os.path.dirname(__file__)

nn_r_e_dirname: str = os.path.join(dirname, "nn_r_e_pressure_local_stencil")
integration_r_e_dirname: str = os.path.join(
    dirname, "integration_r_e_pressure_local_stencil"
)
os.makedirs(integration_r_e_dirname, exist_ok=True)


# Integration
integration.recompile_flow(
    os.path.join(nn_r_e_dirname, "scalings.csv"),
    "local_stencil",
    runspecs_integration["constants"]["OPM"],
    standard_well_file="local_stencil",
    stencil_size=3,
    cell_feature_names=["pressure"],
)

runspecs_integration["variables"].update(
    {"ML_MODEL_PATH": [os.path.join(nn_r_e_dirname, "WI.model"), "", ""]}
)
integration.run_integration(
    runspecs_integration,
    integration_r_e_dirname,
    os.path.join(dirname, "integration.mako"),
)
