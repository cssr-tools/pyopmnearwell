#!/usr/bin/env python

""""
Script to write the saturation functions
"""

import numpy as np


def krwe(sew, krw, nkr):
    # Wetting relative permeability
    return ${dic['krwf'].strip()}


def krce(sew, krc, nkr):
    # CO2 relative permeability
    return ${dic['krnf'].strip()}


def pcwce(sew, pec, npe):
    # Capillary pressure
    return ${dic['pcwcf'].strip()}


def safu_evaluation():
    # Saturation function assignation

    # Properties: srw, 1 - sg, krw, krg, pe
    safu = [[0.0] * 10 for _ in range(${len(dic['safu'])})]
    % for i, _ in enumerate(dic['safu']):
    % for j, _ in enumerate(dic['safu'][i]):
    safu[${i}][${j}] = ${dic['safu'][i][j]}
    % endfor
    % endfor

    with open(
        "${dic['exe']}/${dic['fol']}/preprocessing/TABLES.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("SGFN\n")
        for _, para in enumerate(safu):
            sco2 = np.linspace(0, 1 - para[0], 399)
            sew = abs((1 - sco2 - para[0]) / (1. - para[0]))
            if sco2[0] > 0:
                file.write(
                    f"0.00000 {krce(sew[0], para[3], para[6]) :E}"
                    f" 0.00000 \n"
                )
            for i, value in enumerate(sco2[:-1]):
                file.write(
                    f"{value:E} {krce(sew[i], para[3], para[6]) :E}"
                    f" 0.00000 \n"
                )
            file.write(
                    f"{sco2[-1]:E} {krce(sew[-1], para[3], para[6]) :E}"
                    f" 0.00000 \n"
                )
            file.write("/\n")
        file.write("SWFN\n")
        for _, para in enumerate(safu):
            swatc = np.linspace(0, 1., 10001)
            sls=para[9]
            for i, value in enumerate(swatc):
                if value <= sls:
                    file.write(
                        f"{value:E}"
                        f" 0.00000"
                        f"{10.**((sls-value)*(np.log((sls)/(sls-para[0])*((1.-para[7])/para[7])*(1./(1.-((sls- para[0])/(1 - para[0]))**(1./para[7])))))/(sls)+np.log10(pcwce((sls- para[0])/(1 - para[0]), para[4], para[7]))) : E} \n"
                    )
                elif value >= 1-para[1]:
                    file.write(
                        f"{value:E}"
                        f" 1.00000"
                        f"{pcwce(max((value - para[0]) / (1. - para[0]), para[8]), para[4], para[7]) : E} \n"
                    )
                else:
                    file.write(
                        f"{value:E}"
                        f" {krwe((value-para[0])/(1-para[1] - para[0]), para[2], para[5]) :E}"
                        f"{pcwce(max((value - para[0]) / (1. -para[0]), para[8]), para[4], para[7]) : E} \n"
                    )
            file.write("/\n")


if __name__ == "__main__":
    safu_evaluation()

