<%
import math as mt
import numpy as np
%>
-- Copyright (C) 2023 NORCE
PERMFACT
% if dic['permfact'][0] == "default":
0.0 ${((dic['permfact'][2] - (dic['permfact'][2] - dic['permfact'][4])) / (1 - (dic['permfact'][2] - dic['permfact'][4]))) ** 2 * ((1 - dic['permfact'][1] + dic['permfact'][1]/(1 + (1/dic['permfact'][1])/(1/(dic['permfact'][2] - dic['permfact'][4]) - 1))**2)) / (1 - dic['permfact'][1] + dic['permfact'][1] * ((dic['permfact'][2] - (dic['permfact'][2] - dic['permfact'][4])) / (1 - (dic['permfact'][2] - dic['permfact'][4])) / ((dic['permfact'][2] - (dic['permfact'][2] - dic['permfact'][4])) / (1 - (dic['permfact'][2] - dic['permfact'][4])) + (1 + (1/dic['permfact'][1])/(1/(dic['permfact'][2] - dic['permfact'][4]) - 1)) - 1)) ** 2)}
% for poro_fac in np.linspace(dic['permfact'][2], 1, mt.floor(dic['permfact'][3])):
${poro_fac} ${((poro_fac - (dic['permfact'][2] - dic['permfact'][4])) / (1 - (dic['permfact'][2] - dic['permfact'][4]))) ** 2 * ((1 - dic['permfact'][1] + dic['permfact'][1]/(1 + (1/dic['permfact'][1])/(1/(dic['permfact'][2] - dic['permfact'][4]) - 1))**2)) / (1 - dic['permfact'][1] + dic['permfact'][1] * ((poro_fac - (dic['permfact'][2] - dic['permfact'][4])) / (1 - (dic['permfact'][2] - dic['permfact'][4])) / ((poro_fac - (dic['permfact'][2] - dic['permfact'][4])) / (1 - (dic['permfact'][2] - dic['permfact'][4])) + (1 + (1/dic['permfact'][1])/(1/(dic['permfact'][2] - dic['permfact'][4]) - 1)) - 1)) ** 2)}
% endfor
% else:
0.0 ${( dic['permfact'][4] / (1 - (dic['permfact'][2] - dic['permfact'][4]))) ** dic['permfact'][1]}
% for poro_fac in np.linspace(dic['permfact'][2], 1, mt.floor(dic['permfact'][3])):
${poro_fac} ${((poro_fac - (dic['permfact'][2] - dic['permfact'][4])) / (1 - (dic['permfact'][2] - dic['permfact'][4]))) ** dic['permfact'][1]}
% endfor
% endif
/
/