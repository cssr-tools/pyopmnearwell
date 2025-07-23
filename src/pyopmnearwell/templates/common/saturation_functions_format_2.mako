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
    safug = [[0.0] * ${len(dic['safu'][0])} for _ in range(${len(dic['safu'])})]
    safuw = [[0.0] * ${len(dic['safu'][0])} for _ in range(${len(dic['safu'])})]
    % for i, _ in enumerate(dic['safu']):
    % for j, _ in enumerate(dic['safu'][i]):
    safug[${i}][${j}] = ${dic['safu'][i][j]}
    % if dic["imbnum"]==2 and j==1 and len(dic['safu'])/dic["imbnum"] <= i:
    safuw[${i}][${j}] = ${dic['safu'][int(i%len(dic['safu'])/dic["imbnum"])][j]}
    % else:
    safuw[${i}][${j}] = ${dic['safu'][i][j]}
    % endif
    % endfor
    % endfor

    with open(
        "${dic['fprep']}/TABLES.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("SGFN\n")
        for j, para in enumerate(safug):
            if j>0:
                if safug[j-1]==para:
                    file.write("/\n")
                    continue
            sco2 = np.linspace(para[1], 1 - para[0], para[10])
            if sco2[0]>0:
                file.write(f"{0:E} {0:E} {0:E}\n")
            for i, value in enumerate(sco2[:-1]):
                file.write(
                    f"{value:E} {max(0,krne(1-sco2[i], para[0], para[1], para[3], para[6])):E}"
                    f" {0:E} \n"
                )
            file.write(
                    f"{sco2[-1]:E} {max(0,krne(1-sco2[-1], para[0], para[1], para[3], para[6])):E}"
                    f" {0:E} \n"
                )
            file.write("/\n")
        file.write("SWFN\n")
        for j, para in enumerate(safuw):
            if j>0:
                if safuw[j-1]==para:
                    file.write("/\n")
                    continue
            if para[9]==1. or  para[9]==0. :
                swatc = np.linspace((1.-para[9])*para[0], 1-0*para[1], para[10])
                for i, value in enumerate(swatc):
                    if value <= para[0]:
                        file.write(
                            f"{value:E} {0:E}"
                            f" {pcwce(value, (1.-para[9])*para[0] - para[8], para[1], para[4], para[7]):E} \n"
                        )
                    elif value >= 1 - para[1]:
                        file.write(
                                f"{value:E} {1:E}"
                                f" {pcwce(value, (1.-para[9])*para[0]- para[8], para[1], para[4], para[7]):E} \n"
                            )
                    else:
                        file.write(
                            f"{value:E}"
                            f" {krwe(value, para[0], para[1] , para[2], para[5]):E}"
                            f" {pcwce(value, (1.-para[9])*para[0]- para[8], para[1], para[4], para[7]):E} \n"
                        )
            else:
                swatc = np.linspace(0, 1, para[10])
                sls=para[9]
                for i, value in enumerate(swatc):
                    if value <= sls:
                        file.write(
                            f"{value:E}"
                            f" {krwe(max(value, para[0]), para[0], para[1] , para[2], para[5]):E}"
                            % if dic['pcap'].strip()=="pen * (((sw - swi) / (1. - swi)) ** (-(1./npen)) - 1.) ** (1. - npen)":
                            f" {10.**((sls-value)*(np.log((sls)/(sls-para[0])*((1.-para[7])/para[7])*(1./(1.-((sls- para[0])/(1 - para[0]))**(1./para[7])))))/(sls)+np.log10(pcwce(sls, para[0], para[1], para[4], para[7]))):E} \n"
                            % else:
                            f" {10.**((sls-value)*(np.log((sls)/((sls-para[0])*para[7])))/(sls)+np.log10(pcwce(sls, para[0], para[1], para[4], para[7]))):E} \n"
                            % endif
                        )
                    elif value >= 1 - para[1]:
                        file.write(
                                f"{value:E} {1:E}"
                                f" {pcwce(value, para[0], para[1], para[4], para[7]):E} \n"
                            )
                    else:
                        file.write(
                            f"{value:E}"
                            f" {krwe(value, para[0], para[1] , para[2], para[5]):E}"
                            f" {pcwce(value, para[0], para[1], para[4], para[7]):E} \n"
                        )
            file.write("/\n")


if __name__=="__main__":
    safu_evaluation()
