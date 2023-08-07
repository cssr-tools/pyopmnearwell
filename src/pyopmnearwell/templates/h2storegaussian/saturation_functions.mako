# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python

""""
Script to write the saturation functions
"""

import numpy as np


def krwe(sw, swi, sni, krw, nkr):
    # Wetting relative permeability
    return ${dic['krwf'].strip()}


def krne(sw, swi, sni, krn, nkr):
    # CO2 relative permeability
    return ${dic['krnf'].strip()}


def pcwce(sw, swi, sni, pec, npe):
    # Capillary pressure
    return ${dic['pcwcf'].strip()}


def safu_evaluation():
    # Saturation function assignation

    # Properties: swi, sni, krw, krn, pe
    safu = [[0.0] * 8 for _ in range(${len(dic['safu'])})]
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
        file.write("SGOF\n")
        for _, para in enumerate(safu):
            snatc = np.linspace(para[1], 1-para[0], 10000)
            if para[1] > 0:
                file.write(
                    f"{0:.6f}"
                    f" 0.00000"
                    f" 1.00000"
                    f" {pcwce(1-para[1]+para[7],para[0], para[1], para[4], para[6]):E} \n"
                )
            for i, value in enumerate(snatc):
                if i==0:
                    file.write(
                        f"{value:.6f}"
                        f" 0.00000"
                        f" 1.00000"
                        f" {pcwce(1-value+para[7],para[0], para[1], para[4], para[6]):E} \n"
                    )
                else:
                    file.write(
                        f"{value:.6f}"
                        f" {krne(1-value,para[0], para[1] , para[2], para[5]) :.6f}"
                        f" {krwe(1-value,para[0], para[1] , para[2], para[5]) :.6f}"
                        f" {pcwce(1-value+para[7],para[0], para[1], para[4], para[6]):E} \n"
                    )
            file.write("/\n")

if __name__ == "__main__":
    safu_evaluation()
