<%
import math as mt
import numpy as np
%>
-- Copyright (C) 2023 NORCE
PCFACT
0.0 ${(dic['pcfact'][1]/(((dic['pcfact'][1] - (dic['pcfact'][1] - dic['pcfact'][3])) / (1 - (dic['pcfact'][1] - dic['pcfact'][3]))) ** 2 * ((1 - dic['pcfact'][0] + dic['pcfact'][0]/(1 + (1/dic['pcfact'][0])/(1/(dic['pcfact'][1] - dic['pcfact'][3]) - 1))**2)) / (1 - dic['pcfact'][0] + dic['pcfact'][0] * ((dic['pcfact'][1] - (dic['pcfact'][1] - dic['pcfact'][3])) / (1 - (dic['pcfact'][1] - dic['pcfact'][3])) / ((dic['pcfact'][1] - (dic['pcfact'][1] - dic['pcfact'][3])) / (1 - (dic['pcfact'][1] - dic['pcfact'][3])) + (1 + (1/dic['pcfact'][0])/(1/(dic['pcfact'][1] - dic['pcfact'][3]) - 1)) - 1)) ** 2))) ** dic['pcfact'][4]}
% for poro_fac in np.linspace(dic['pcfact'][1], 1, mt.floor(dic['pcfact'][2])):
${poro_fac} ${(poro_fac/(((poro_fac - (dic['pcfact'][1] - dic['pcfact'][3])) / (1 - (dic['pcfact'][1] - dic['pcfact'][3]))) ** 2 * ((1 - dic['pcfact'][0] + dic['pcfact'][0]/(1 + (1/dic['pcfact'][0])/(1/(dic['pcfact'][1] - dic['pcfact'][3]) - 1))**2)) / (1 - dic['pcfact'][0] + dic['pcfact'][0] * ((poro_fac - (dic['pcfact'][1] - dic['pcfact'][3])) / (1 - (dic['pcfact'][1] - dic['pcfact'][3])) / ((poro_fac - (dic['pcfact'][1] - dic['pcfact'][3])) / (1 - (dic['pcfact'][1] - dic['pcfact'][3])) + (1 + (1/dic['pcfact'][0])/(1/(dic['pcfact'][1] - dic['pcfact'][3]) - 1)) - 1)) ** 2))) ** dic['pcfact'][4]}
% endfor  
/
/