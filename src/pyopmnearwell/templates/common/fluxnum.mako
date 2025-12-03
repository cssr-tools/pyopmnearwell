<%
import math as mt
import numpy as np
n = 1
val = dic["layers"][0]+1
%>\
EQUALS
% for i in range(dic['nocells'][2]):
% if val != dic["layers"][i]+1:
FLUXNUM ${int(val)} 4* ${"".join([' ' for _ in range(dic["whnz"]-len(str(n)))])}${n} ${"".join([' ' for _ in range(dic["whnz"]-len(str(i)))])}${i} /
<%
val = dic["layers"][i]+1
n = i + 1
%>\
% elif loop.last:
FLUXNUM ${int(dic["layers"][i]+1)} 4* ${"".join([' ' for _ in range(dic["whnz"]-len(str(n)))])}${n} ${"".join([' ' for _ in range(dic["whnz"]-len(str(i+1)))])}${i+1} /
% endif
% endfor
% if dic['perforations'][0]==1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] not in ['cartesian','cpg3d','coord3d','tensor3d']:
FLUXNUM ${dic['satnum']+1} 1 ${np.sum(dic['x_centers']<dic['perforations'][2])} 2* ${"".join([' ' for _ in range(dic["whnz"]-len(str((i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1)))))])}${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${"".join([' ' for _ in range(dic["whnz"]-len(str((i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1)))))])}${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
% else:
FLUXNUM ${dic['satnum']+1} ${mt.ceil(dic["nocells"][1] / 2)-np.sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + np.sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2)-np.sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + np.sum(dic['x_centers']<dic['perforations'][2])} ${"".join([' ' for _ in range(dic["whnz"]-len(str((i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1)))))])}${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${"".join([' ' for _ in range(dic["whnz"]-len(str((i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1)))))])}${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
% endif
% endfor
% endif
/