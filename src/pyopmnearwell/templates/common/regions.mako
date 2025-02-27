<%
import math as mt
%>
-- Copyright (C) 2023 NORCE

EQUALS
% for i in range(dic['nocells'][2]):
SATNUM ${mt.floor(dic["layers"][i]+1)} 4* ${i+1} ${i+1} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] not in ['cartesian','cpg3d','coord3d','tensor3d']:
SATNUM ${dic['satnum']+1} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 2* ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
% else:
SATNUM ${dic['satnum']+1} ${mt.ceil(dic["nocells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
% endif
% endfor
% endif
/

% if dic["hysteresis"]!=0:
EQUALS
% for i in range(dic['nocells'][2]):
IMBNUM ${dic['satnum']+dic['perforations'][0]+mt.floor(dic["layers"][i]+1)} 4* ${i+1} ${i+1} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] not in ['cartesian','cpg3d','coord3d','tensor3d']:
IMBNUM ${2*dic['satnum']+2} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 2* ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
%else:
IMBNUM ${2*dic['satnum']+2} ${mt.ceil(dic["nocells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/
% endif