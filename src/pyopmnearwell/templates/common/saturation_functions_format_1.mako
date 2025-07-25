# SPDX-FileCopyrightText: 2023-2025, NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python

"""
Script to write the saturation functions
"""

import numpy as np


def krwe(sw, swi, sni, krw, nkrw):
    # Wetting relative permeability
    return ${dic['krw'].strip()}


def krne(sw, swi, sni, krn, nkrn):
    # CO2 relative permeability
    return ${dic['krn'].strip()}


def pcwce(sw, swi, sni, pen, npen):
    # Capillary pressure
    return 0 if pen==0 else ${dic['pcap'].strip()}


def safu_evaluation():
    # Saturation function assignation

    # Properties: swi, sni, krw, krn, pe
    safu = [[0.0] * ${len(dic['safu'][0])} for _ in range(${len(dic['safu'])})]
    % for i, _ in enumerate(dic['safu']):
    % for j, _ in enumerate(dic['safu'][i]):
    safu[${i}][${j}] = ${dic['safu'][i][j]}
    % endfor
    % endfor

    with open(
        "${dic['fprep']}/TABLES.INC",
        "w",
        encoding="utf8",
    ) as file:
    file.write("SGOF\n")
        for j, para in enumerate(safu):
            if j>0:
                if safu[j-1]==para:
                    file.write("/\n")
                    continue
            snatc = np.linspace(para[1], 1-para[0], para[10])
            if para[1]>0:
                file.write(
                    f"{0:E} {0:E} {1:E}"
                    f" {pcwce(1-para[1]+para[8],para[0], para[1], para[4], para[7]):E} \n"
                )
            for i, value in enumerate(snatc):
                if i==0:
                    file.write(
                        f"{value:E} {0:E}"
                        f" {krwe(1-value,para[0], para[1] , para[2], para[5]) :.6f}"
                        f" {pcwce(1-value+para[8],para[0], para[1], para[4], para[7]):E} \n"
                    )
                else:
                    file.write(
                        f"{value:E}"
                        f" {krne(1-value,para[0], para[1] , para[3], para[6]) :.6f}"
                        f" {krwe(1-value,para[0], para[1] , para[2], para[5]) :.6f}"
                        f" {pcwce(1-value+para[8],para[0], para[1], para[4], para[7]):E} \n"
                    )
            file.write("/\n")

if __name__=="__main__":
    safu_evaluation()
