# SPDX-FileCopyrightText: 2023 NORCE
# SPDX-License-Identifier: GPL-3.0

 

""""
Script to run Flow for a random input variable
"""

 

import os
import numpy as np
from ecl.summary import EclSum
from ecl.eclfile import EclFile
from mako.template import Template
import matplotlib
import matplotlib.pyplot as plt
import math

 

def computePeaceman(h: float, k: float, r_e: float, r_w: float) -> float:
    r"""Compute the well productivity index (adjusted for density and viscosity) from the
    Peaceman well model.

 

    .. math::
        WI\cdot\frac{\mu}{\rho} = \frac{2\pi hk}{\ln (r_e/r_w)}

 

    Parameters:
        h: Thickness of the well block.
        k: Permeability.
        r_e: Equivalent well-block radius.
        r_w: Wellbore radius.

 

    Returns:
        :math:`WI\cdot\frac{\mu}{\rho}`

 

    """
    WI = (2 * math.pi * h * k) / (math.log(r_e / r_w))
    return WI

np.random.seed(7)

 

xmx = np.load("./output/output/xspace.npy")
re = 0.5 * (xmx[2:] + xmx[1:-1])
#re = re + 1.0
print(re)
h = 1
k = 1013.25*9.869233E-16
#rw = 0.1/2+1.0
rw = 0.05
wi2 = []
b = 1.0
mu = 0.6532*0.001 
for r in re:
  wi2.append(computePeaceman(h, k, r, rw)*b/mu)

 

densr = 998.108
qrate = 6*1.001896E+01/86400
wbhp = []
wi = []
fig, axis = plt.subplots()
axis.set_yscale("log")
rst = EclFile(f"./output/output/RESERVOIR.UNRST")
pressure = np.array(rst.iget_kw("PRESSURE")[-1])
pw = pressure[0]
wi = qrate/((pw - pressure[1:])*1e5)
print(len(pressure), len(re))
#print(pressure, wi2/wi)
print(wbhp, pressure[0])
axis.plot(
    re,
    wi,
    color=matplotlib.colormaps["tab20"].colors[0],
    linestyle="",
    marker="*",
    markersize=5,
    label='sim',
)
axis.plot(
    re,
    wi2,
    color=matplotlib.colormaps["tab20"].colors[1],
    linestyle="",
    marker=".",
    markersize=5,
    label='peaceman'
)
axis.set_ylabel("WI [kg/(Bar day)]", fontsize=12)
axis.set_xlabel("Distance to well [m]", fontsize=12)
axis.legend(fontsize=6)

 

fig.savefig("re.png")
np.save('re', re)
np.save('wi', wi)