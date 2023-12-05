<%
import math as mt
import numpy as np
%>
-- Copyright (C) 2023 NORCE
PERMFACT
% if dic["poro-perm"] == "default":
0.0 ${((dic['salt_props'][4] - (dic['salt_props'][4] - dic['salt_props'][6])) / (1 - (dic['salt_props'][4] - dic['salt_props'][6]))) ** 2 * ((1 - dic['salt_props'][3] + dic['salt_props'][3]/(1 + (1/dic['salt_props'][3])/(1/(dic['salt_props'][4] - dic['salt_props'][6]) - 1))**2)) / (1 - dic['salt_props'][3] + dic['salt_props'][3] * ((dic['salt_props'][4] - (dic['salt_props'][4] - dic['salt_props'][6])) / (1 - (dic['salt_props'][4] - dic['salt_props'][6])) / ((dic['salt_props'][4] - (dic['salt_props'][4] - dic['salt_props'][6])) / (1 - (dic['salt_props'][4] - dic['salt_props'][6])) + (1 + (1/dic['salt_props'][3])/(1/(dic['salt_props'][4] - dic['salt_props'][6]) - 1)) - 1)) ** 2)}
% for poro_fac in np.linspace(dic['salt_props'][4], 1, mt.floor(dic['salt_props'][5])):
${poro_fac} ${((poro_fac - (dic['salt_props'][4] - dic['salt_props'][6])) / (1 - (dic['salt_props'][4] - dic['salt_props'][6]))) ** 2 * ((1 - dic['salt_props'][3] + dic['salt_props'][3]/(1 + (1/dic['salt_props'][3])/(1/(dic['salt_props'][4] - dic['salt_props'][6]) - 1))**2)) / (1 - dic['salt_props'][3] + dic['salt_props'][3] * ((poro_fac - (dic['salt_props'][4] - dic['salt_props'][6])) / (1 - (dic['salt_props'][4] - dic['salt_props'][6])) / ((poro_fac - (dic['salt_props'][4] - dic['salt_props'][6])) / (1 - (dic['salt_props'][4] - dic['salt_props'][6])) + (1 + (1/dic['salt_props'][3])/(1/(dic['salt_props'][4] - dic['salt_props'][6]) - 1)) - 1)) ** 2)}
% endfor
% else:
0.0 ${( dic['salt_props'][6] / (1 - (dic['salt_props'][4] - dic['salt_props'][6]))) ** dic['salt_props'][3]}
% for poro_fac in np.linspace(dic['salt_props'][4], 1, mt.floor(dic['salt_props'][5])):
${poro_fac} ${((poro_fac - (dic['salt_props'][4] - dic['salt_props'][6])) / (1 - (dic['salt_props'][4] - dic['salt_props'][6]))) ** dic['salt_props'][3]}
% endfor
% endif
/
/