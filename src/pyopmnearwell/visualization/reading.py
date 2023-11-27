# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

# pylint: skip-file
""""
Script to read the output files
"""

import pathlib

import numpy as np
import pandas as pd

try:
    from opm.io.ecl import EclFile as EclFileOpm
    from opm.io.ecl import ERst, ESmry
except ImportError:
    print("The opm Python package was not found, using ecl")
try:
    from ecl.eclfile import EclFile
    from ecl.grid import EclGrid
    from ecl.summary import EclSum
except ImportError:
    print("The ecl Python package was not found, using opm")


def read_simulations(dic):
    """
    Function to read the generated output files

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic["connections"] = []
    if dic["plot"] == "ecl":
        dic = read_ecl(dic)
    else:
        dic = read_opm(dic)
    return dic


def read_opm(dic):
    """
    Function to read the output files using the Python opm package

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    for study in dic["folders"]:
        dic[f"{study}_rst_seconds"] = np.load(
            dic["exe"] + "/" + study + "/output/schedule.npy"
        )
        dic[f"{study}_wellid"] = np.load(
            dic["exe"] + "/" + study + "/output/position.npy"
        )
        dic[f"{study}_radius"] = np.load(
            dic["exe"] + "/" + study + "/output/radius.npy"
        )
        dic[f"{study}_angle"] = np.load(dic["exe"] + "/" + study + "/output/angle.npy")
        deck = [
            f.stem
            for f in (pathlib.Path(dic["exe"]) / study / "output").iterdir()
            if str(f).endswith(".UNRST")
        ]
        case = str(pathlib.Path(dic["exe"]) / study / f"output/{deck[0]}")
        dic[f"{study}_rst"] = ERst(case + ".UNRST")
        dic[f"{study}_ini"] = EclFileOpm(case + ".INIT")
        dic[f"{study}_smsp"] = ESmry(case + ".SMSPEC")
        dic[f"{study}_permeability_array"] = [dic[f"{study}_ini"]["PERMX"]]
        dic[f"{study}_porosity_array"] = [dic[f"{study}_ini"]["PORO"]]
        dic[f"{study}_porv_array"] = [dic[f"{study}_ini"]["PORV"]]
        dic[f"{study}_satnum_array"] = [dic[f"{study}_ini"]["SATNUM"]]
        dic[f"{study}_injection_raten"] = dic[f"{study}_smsp"]["FGIR"]
        if dic[f"{study}_rst"].count("SWAT", 0):
            dic[f"{study}_injection_ratew"] = dic[f"{study}_smsp"]["FWIR"]
            dic[f"{study}_rhon_ref"] = 1.86843  # CO2 reference density
            dic[f"{study}_rhow_ref"] = 998.108  # Water reference density
            dic[f"{study}_rhor"] = dic[f"{study}_rhon_ref"]
        else:
            dic[f"{study}_injection_ratew"] = dic[f"{study}_smsp"]["FOIR"]
            dic[f"{study}_rhon_ref"] = 0.0850397  # H2 reference density
            # dic[f"{study}_rhow_ref"] = 0.6785064  # CH4 reference density
            dic[f"{study}_rhow_ref"] = 998.108  # Water reference density
            dic[f"{study}_rhor"] = dic[f"{study}_rhow_ref"]
        dic[f"{study}_well_pressure"] = dic[f"{study}_smsp"]["WBHP:INJ0"]
        dic[f"{study}_well_pi"] = dic[f"{study}_smsp"]["WPI:INJ0"]
        dic[f"{study}_smsp_seconds"] = 86400 * dic[f"{study}_smsp"]["TIME"]
        dic[f"{study}_report_time"] = dic[f"{study}_smsp"]["YEARS", True]
        dic[f"{study}_report_time"] = np.insert(dic[f"{study}_report_time"], 0, 0)
        dic[f"{study}_smsp_rst"] = [
            pd.Series(abs(dic[f"{study}_smsp_seconds"] - time)).argmin()
            for time in dic[f"{study}_rst_seconds"]
        ]
        dic[f"{study}_smsp_seconds"] = np.insert(dic[f"{study}_smsp_seconds"], 0, 0.0)
        dic[f"{study}_indicator_array"] = []
        dic[f"{study}_viscw_array"] = []
        dic[f"{study}_denw_array"] = []
        dic[f"{study}_viscn_array"] = []
        dic[f"{study}_denn_array"] = []
        dic[f"{study}_concentration_array"] = []
        dic = create_arrays_opm(dic, study)
        if dic[f"{study}_injection_ratew"][-1] > 0:
            dic[f"{study}_Q"] = (
                dic[f"{study}_injection_ratew"][-1] * dic[f"{study}_rhow_ref"]
            )
            dic[f"{study}_Qrho"] = (
                dic[f"{study}_injection_ratew"][-1]
                * dic[f"{study}_rhow_ref"]
                / dic[f"{study}_denw_array"][-1][dic[f"{study}_wellid"]]
            )
            dic[f"{study}_mu"] = dic[f"{study}_viscw_array"][-1][dic[f"{study}_wellid"]]
            dic[f"{study}_rho"] = (
                dic[f"{study}_rhow_ref"]
                * dic[f"{study}_denw_array"][-1][dic[f"{study}_wellid"]]
            )
        else:
            dic[f"{study}_Q"] = (
                dic[f"{study}_injection_raten"][-1] * dic[f"{study}_rhon_ref"]
            )
            dic[f"{study}_Qrho"] = (
                dic[f"{study}_injection_raten"][-1]
                * dic[f"{study}_rhon_ref"]
                / dic[f"{study}_denn_array"][-1][dic[f"{study}_wellid"]]
            )
            dic[f"{study}_mu"] = dic[f"{study}_viscn_array"][-1][dic[f"{study}_wellid"]]
            dic[f"{study}_rho"] = (
                dic[f"{study}_rhon_ref"]
                * dic[f"{study}_denn_array"][-1][dic[f"{study}_wellid"]]
            )
        dic[f"{study}_WI"] = (dic[f"{study}_Q"]) / (
            dic[f"{study}_well_pressure"][-1]
            - dic[f"{study}_pressure_array"][-1][dic[f"{study}_wellid"]]
        )
        dic[f"{study}_T"] = (
            1.01324997e15
            * (1e5 * dic[f"{study}_WI"] / 86400.0)
            * (1e-3 * dic[f"{study}_mu"])
            / dic[f"{study}_rho"]
        )
    return dic


def create_arrays_opm(dic, study):
    """
    Function to create the required numpy arrays

    Args:
        dic (dict): Global dictionary with required parameters

    """
    dic[f"{study}_totalsaltprec"] = []
    for quantity in dic["quantity"]:
        dic[f"{study}_{quantity}_array"] = []
        for rst in dic[f"{study}_rst"].report_steps:
            if quantity == "salt":
                if dic[f"{study}_rst"].count("SALTP", 0):
                    dic[f"{study}_{quantity}_array"].append(
                        np.array(dic[f"{study}_rst"]["SALTP", rst])
                    )
                    dic[f"{study}_totalsaltprec"].append(
                        (
                            np.array(dic[f"{study}_rst"]["SALTP", rst])
                            * np.array(dic[f"{study}_porv_array"])
                            * 2153
                        ).sum()
                    )
                else:
                    dic[f"{study}_{quantity}_array"].append(
                        np.array(0 * dic[f"{study}_rst"]["SGAS", rst])
                    )
            if quantity == "permfact":
                if dic[f"{study}_rst"].count("PERMFACT", 0):
                    dic[f"{study}_{quantity}_array"].append(
                        np.array(dic[f"{study}_rst"]["PERMFACT", rst])
                    )
                else:
                    dic[f"{study}_{quantity}_array"].append(
                        -1.0 < np.array(dic[f"{study}_rst"]["SGAS", rst])
                    )
            if quantity == "saturation":
                dic[f"{study}_indicator_array"].append(
                    np.array(dic[f"{study}_rst"]["SGAS", rst]) > dic["sat_thr"]
                )
                dic[f"{study}_{quantity}_array"].append(
                    np.array(dic[f"{study}_rst"]["SGAS", rst])
                )
                dic[f"{study}_viscn_array"].append(
                    np.array(dic[f"{study}_rst"]["GAS_VISC", rst])
                )
                dic[f"{study}_denn_array"].append(
                    np.array(dic[f"{study}_rst"]["GAS_DEN", rst])
                )
            if quantity == "pressure":
                dic[f"{study}_{quantity}_array"].append(
                    np.array(dic[f"{study}_rst"]["PRESSURE", rst])
                )
                if dic[f"{study}_rst"].count("SWAT", 0):
                    dic[f"{study}_viscw_array"].append(
                        np.array(dic[f"{study}_rst"]["WAT_VISC", rst])
                    )
                    dic[f"{study}_denw_array"].append(
                        np.array(dic[f"{study}_rst"]["WAT_DEN", rst])
                    )
                    dic[f"{study}_concentration_array"].append(
                        np.array(dic[f"{study}_rhor"] * dic[f"{study}_rst"]["RSW", rst])
                    )
                else:
                    dic[f"{study}_viscw_array"].append(
                        np.array(dic[f"{study}_rst"]["OIL_VISC", rst])
                    )
                    dic[f"{study}_denw_array"].append(
                        np.array(dic[f"{study}_rst"]["OIL_DEN", rst])
                    )
                    dic[f"{study}_concentration_array"].append(
                        np.array(dic[f"{study}_rhor"] * dic[f"{study}_rst"]["RV", rst])
                    )
    return dic


def read_ecl(dic):
    """
    Function to read the output files using the Python ecl package

    Args:
        dic (dict): Global dictionary with required parameters

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    for study in dic["folders"]:
        dic[f"{study}_rst_seconds"] = np.load(
            dic["exe"] + "/" + study + "/output/schedule.npy"
        )
        dic[f"{study}_wellid"] = np.load(
            dic["exe"] + "/" + study + "/output/position.npy"
        )
        dic[f"{study}_radius"] = np.load(
            dic["exe"] + "/" + study + "/output/radius.npy"
        )
        dic[f"{study}_angle"] = np.load(dic["exe"] + "/" + study + "/output/angle.npy")
        deck = [
            f.stem
            for f in (pathlib.Path(dic["exe"]) / study / "output").iterdir()
            if str(f).endswith(".UNRST")
        ]
        case = str(pathlib.Path(dic["exe"]) / study / f"output/{deck[0]}")
        dic[f"{study}_rst"] = EclFile(case + ".UNRST")
        dic[f"{study}_ini"] = EclFile(case + ".INIT")
        dic[f"{study}_grid"] = EclGrid(case + ".EGRID")
        dic[f"{study}_smsp"] = EclSum(case + ".SMSPEC")
        if dic[f"{study}_smsp"].has_key("CGIR:INJ0:1,1,1"):
            dic["connections"] = 1
        dic[f"{study}_saturation"] = dic[f"{study}_rst"].iget_kw("SGAS")
        if dic[f"{study}_rst"].has_kw("SALTP"):
            dic[f"{study}_salt"] = dic[f"{study}_rst"].iget_kw("SALTP")
            dic[f"{study}_permfact"] = dic[f"{study}_rst"].iget_kw("PERMFACT")
            salt = 1.0
        else:
            dic[f"{study}_salt"] = dic[f"{study}_rst"].iget_kw("PRESSURE")
            dic[f"{study}_permfact"] = dic[f"{study}_rst"].iget_kw("PRESSURE")
            salt = 0.0
        dic[f"{study}_pressure"] = dic[f"{study}_rst"].iget_kw("PRESSURE")
        dic[f"{study}_permeability_array"] = [dic[f"{study}_ini"].iget_kw("PERMX")[0]]
        dic[f"{study}_porosity_array"] = [dic[f"{study}_ini"]["PORO"][0]]
        dic[f"{study}_porv_array"] = [dic[f"{study}_ini"]["PORV"][0]]
        dic[f"{study}_satnum_array"] = [dic[f"{study}_ini"]["SATNUM"][0]]
        dic[f"{study}_viscg"] = dic[f"{study}_rst"].iget_kw("GAS_VISC")
        dic[f"{study}_deng"] = dic[f"{study}_rst"].iget_kw("GAS_DEN")
        dic[f"{study}_injection_raten"] = dic[f"{study}_smsp"]["FGIR"].values
        if dic[f"{study}_rst"].has_kw("SWAT"):
            dic[f"{study}_viscl"] = dic[f"{study}_rst"].iget_kw("WAT_VISC")
            dic[f"{study}_denl"] = dic[f"{study}_rst"].iget_kw("WAT_DEN")
            dic[f"{study}_rs"] = dic[f"{study}_rst"].iget_kw("RSW")
            dic[f"{study}_rhon_ref"] = 1.86843  # CO2 reference density
            dic[f"{study}_rhow_ref"] = 998.108  # Water reference density
            dic[f"{study}_rhor"] = dic[f"{study}_rhon_ref"]
            dic[f"{study}_injection_ratew"] = dic[f"{study}_smsp"]["FWIR"].values
        else:
            dic[f"{study}_viscl"] = dic[f"{study}_rst"].iget_kw("OIL_VISC")
            dic[f"{study}_denl"] = dic[f"{study}_rst"].iget_kw("OIL_DEN")
            # dic[f"{study}_rs"] = dic[f"{study}_rst"].iget_kw("RV")
            dic[f"{study}_rhon_ref"] = 0.0850397  # H2 reference density
            dic[f"{study}_rhow_ref"] = 998.108  # Water reference density
            # dic[f"{study}_rhow_ref"] = 0.6785064  # CH4 reference density
            dic[f"{study}_rhor"] = dic[f"{study}_rhow_ref"]
            dic[f"{study}_injection_ratew"] = dic[f"{study}_smsp"]["FOIR"].values
        dic[f"{study}_indicator_array"] = []
        dic[f"{study}_well_pressure"] = dic[f"{study}_smsp"]["WBHP:INJ0"].values
        dic[f"{study}_well_pi"] = dic[f"{study}_smsp"]["WPI:INJ0"].values
        dic = handle_smsp_time(dic, study)
        dic = create_arrays_ecl(dic, study, salt)
    return dic


def handle_smsp_time(dic, study):
    """
    Function to chandle the times in the summary files

    Args:
        dic (dict): Global dictionary with required parameters
        str (study): Name of the folder containing the results

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic[f"{study}_smsp_report_step"] = dic[f"{study}_smsp"]["WBHP:INJ0"].report_step
    dic[f"{study}_report_time"] = dic[f"{study}_rst"].dates
    dic[f"{study}_smsp_seconds"] = [
        (dic[f"{study}_smsp"].numpy_dates[i + 1] - dic[f"{study}_smsp"].numpy_dates[i])
        / np.timedelta64(1, "s")
        for i in range(len(dic[f"{study}_smsp"].numpy_dates) - 1)
    ]
    dic[f"{study}_smsp_seconds"].insert(
        0,
        (
            dic[f"{study}_smsp"].numpy_dates[0]
            - np.datetime64(dic[f"{study}_smsp"].get_start_time())
        )
        / np.timedelta64(1, "s"),
    )
    for i in range(len(dic[f"{study}_smsp"].numpy_dates) - 1):
        dic[f"{study}_smsp_seconds"][i + 1] += dic[f"{study}_smsp_seconds"][i]
    dic[f"{study}_smsp_rst"] = [
        pd.Series(abs(dic[f"{study}_smsp_seconds"] - time)).argmin()
        for time in dic[f"{study}_rst_seconds"]
    ]
    dic[f"{study}_smsp_seconds"] = np.insert(dic[f"{study}_smsp_seconds"], 0, 0.0)
    return dic


def create_arrays_ecl(dic, study, salt):
    """
    Function to create the required numpy arrays

    Args:
        dic (dict): Global dictionary with required parameters
        str (study): Name of the folder containing the results
        int (salt): Indicator for salt precipitation

    Returns:
        dic (dict): Global dictionary with new added parameters

    """
    dic[f"{study}_viscn_array"] = []
    dic[f"{study}_denn_array"] = []
    dic[f"{study}_viscw_array"] = []
    dic[f"{study}_denw_array"] = []
    dic[f"{study}_concentration_array"] = []
    dic[f"{study}_totalsaltprec"] = []
    for quantity in dic["quantity"]:
        dic[f"{study}_{quantity}_array"] = []
        for i in range(dic[f"{study}_rst"].num_report_steps()):
            if quantity == "saturation":
                dic[f"{study}_indicator_array"].append(
                    np.array(dic[f"{study}_saturation"][i]) > dic["sat_thr"]
                )
                dic[f"{study}_{quantity}_array"].append(
                    np.array(
                        dic[f"{study}_saturation"][i]
                        * (1.0 - salt * dic[f"{study}_salt"][i])
                    )
                )
                dic[f"{study}_viscn_array"].append(np.array(dic[f"{study}_viscg"][i]))
                dic[f"{study}_denn_array"].append(np.array(dic[f"{study}_deng"][i]))
                if f"{study}_rs" in dic:
                    dic[f"{study}_concentration_array"].append(
                        dic[f"{study}_rhor"] * np.array(dic[f"{study}_rs"][i])
                    )
                else:
                    dic[f"{study}_concentration_array"].append(
                        0 * np.array(dic[f"{study}_deng"][i])
                    )
            if quantity == "salt":
                dic[f"{study}_{quantity}_array"].append(
                    np.array(dic[f"{study}_{quantity}"][i])
                )
                dic[f"{study}_totalsaltprec"].append(
                    (
                        np.array(dic[f"{study}_{quantity}"][i])
                        * np.array(dic[f"{study}_porv_array"])
                        * 2153
                    ).sum()
                )
            if quantity == "permfact":
                dic[f"{study}_{quantity}_array"].append(
                    np.array(dic[f"{study}_{quantity}"][i])
                )
            if quantity == "pressure":
                dic[f"{study}_{quantity}_array"].append(
                    np.array(dic[f"{study}_{quantity}"][i])
                )
                dic[f"{study}_viscw_array"].append(np.array(dic[f"{study}_viscl"][i]))
                dic[f"{study}_denw_array"].append(np.array(dic[f"{study}_denl"][i]))
    if dic[f"{study}_injection_ratew"][-1] > 0:
        dic[f"{study}_Q"] = (
            dic[f"{study}_injection_ratew"][-1] * dic[f"{study}_rhow_ref"]
        )
        dic[f"{study}_Qrho"] = (
            dic[f"{study}_injection_ratew"][-1]
            * dic[f"{study}_rhow_ref"]
            / dic[f"{study}_denw_array"][-1][dic[f"{study}_wellid"]]
        )
        dic[f"{study}_mu"] = dic[f"{study}_viscw_array"][-1][dic[f"{study}_wellid"]]
        dic[f"{study}_rho"] = (
            dic[f"{study}_rhow_ref"]
            * dic[f"{study}_denw_array"][-1][dic[f"{study}_wellid"]]
        )
    else:
        dic[f"{study}_Q"] = (
            dic[f"{study}_injection_raten"][-1] * dic[f"{study}_rhon_ref"]
        )
        dic[f"{study}_Qrho"] = (
            dic[f"{study}_injection_raten"][-1]
            * dic[f"{study}_rhon_ref"]
            / dic[f"{study}_denn_array"][-1][dic[f"{study}_wellid"]]
        )
        dic[f"{study}_mu"] = dic[f"{study}_viscn_array"][-1][dic[f"{study}_wellid"]]
        dic[f"{study}_rho"] = (
            dic[f"{study}_rhon_ref"]
            * dic[f"{study}_denn_array"][-1][dic[f"{study}_wellid"]]
        )
    dic[f"{study}_WI"] = (dic[f"{study}_Q"]) / (
        dic[f"{study}_well_pressure"][-1]
        - dic[f"{study}_pressure_array"][-1][dic[f"{study}_wellid"]]
    )
    dic[f"{study}_T"] = (
        1.01324997e15
        * (1e5 * dic[f"{study}_WI"] / 86400.0)
        * (1e-3 * dic[f"{study}_mu"])
        / dic[f"{study}_rho"]
    )
    return dic
