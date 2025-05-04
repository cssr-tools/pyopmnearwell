# SPDX-FileCopyrightText: 2025 NORCE
# SPDX-License-Identifier: GPL-3.0
#!/usr/bin/env python

<%
names = [val[0] for val in dic['popevals'][0] if val[0] not in ["npoints"]]
vals = ""
parm = ""
for i, name in enumerate(names):
    vals += name
    parm += f"para[{i}]"
    if i < len(names)-1:
        vals += ", "
        parm += ", "
%>

"""
Script to write the Leveret J tables
"""

import numpy as np
import math as mt

def pcfact(pofa, ${vals}):
    # Capillary pressure factor
    return (pofa / ${dic['poroperm'].strip()}) ** ${dic['pcfact']}

def pcfact_evaluation():
    vals = [[0.0] * ${len(dic['popevals'][0])} for _ in range(${len(dic['popevals'])})]
    % for i, _ in enumerate(dic['popevals']):
    % for j, _ in enumerate(dic['popevals'][i]):
    vals[${i}][${j}] = ${dic['popevals'][i][j][1]}
    % endfor
    % endfor
    with open(
        "${dic['fprep']}/PCFACT.INC",
        "w",
        encoding="utf8",
    ) as file:
        file.write("-- Copyright (C) 2025 NORCE\n")
        file.write("PCFACT\n")
        for i, para in enumerate(vals):
            if i > 0:
                if vals[i-1] == para:
                    file.write("/\n")
                    continue
            file.write(f"0.0 {pcfact(para[0], ${parm})}\n")
            for pofa in np.linspace(para[0], 1, mt.floor(para[-1])):
                file.write(f"{pofa} {pcfact(pofa, ${parm})}\n")
            file.write("/\n")
        for i in range(${len(dic['safu'])-len(dic['popevals'])}):
            file.write("/\n")

if __name__ == "__main__":
    pcfact_evaluation()