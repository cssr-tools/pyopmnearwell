# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python

""""
Script to write the saturation functions
"""

import numpy as np


def krwe(sw, swi, sni, krw, nkrw):
    # Wetting relative permeability
    return ${dic['krwf'].strip()}


def krne(sw, swi, sni, krn, nkrn):
    # CO2 relative permeability
    return ${dic['krnf'].strip()}


def pcwce(sw, swi, sni, pec, npe):
    # Capillary pressure
    return ${dic['pcwcf'].strip()}


def safu_evaluation():
    # Saturation function assignation

    # Properties: swi, sni, krw, krn, pe
    safu = [[0.0] * 9 for _ in range(${len(dic['safu'])})]
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
            sco2 = np.linspace(para[1], 1 - para[0], 1001)
            if sco2[0] > 0:
                file.write(
                    f"0.00000 {max(0,krne(1-sco2[0], para[0], para[1], para[3], para[6])):.6f}"
                    f" 0.00000 \n"
                )
            for i, value in enumerate(sco2[:-1]):
                file.write(
                    f"{value:E} {max(0,krne(1-sco2[i], para[0], para[1], para[3], para[6])):.6f}"
                    f" 0.00000 \n"
                )
            file.write(
                    f"{sco2[-1]:E} {max(0,krne(1-sco2[-1], para[0], para[1], para[3], para[6])):.6f}"
                    f" 0.00000 \n"
                )
            file.write("/\n")
        file.write("SWFN\n")
        for _, para in enumerate(safu):
            swatc = np.linspace(para[0], 1-para[1], 10000)
            for i, value in enumerate(swatc):
                if i==0:
                    file.write(
                        f"{value:E}"
                        f" 0.00000"
                        f" {pcwce(value+para[8], para[0], para[1], para[4], para[7]):E} \n"
                    )
                else:
                    file.write(
                        f"{value:E}"
                        f" {krwe(value, para[0], para[1] , para[2], para[5]):E}"
                        f" {pcwce(value + para[8], para[0], para[1], para[4], para[7]):E} \n"
                    )
            file.write("/\n")


if __name__ == "__main__":
    safu_evaluation()
