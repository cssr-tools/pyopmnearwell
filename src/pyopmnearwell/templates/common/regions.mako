<%
import math as mt
%>
-- Copyright (C) 2023 NORCE

EQUALS
% for i in range(dic['noCells'][2]):
SATNUM  ${mt.floor(dic["layers"][i]+1)} 1* 1* 1* 1* ${i+1} ${i+1} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] != 'cartesian':
SATNUM  ${dic['satnum']+1} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 1* 1* ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} /
% else:
SATNUM  ${dic['satnum']+1} ${mt.floor(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} /
% endif
% endfor
% endif
/

% if dic["hysteresis"] ==1:
EQUALS
% for i in range(dic['noCells'][2]):
IMBNUM  ${dic['satnum']+dic['perforations'][0]+mt.floor(dic["layers"][i]+1)} 1* 1* 1* 1* ${i+1} ${i+1} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] != 'cartesian':
IMBNUM  ${2*dic['satnum']+2} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 1* 1* ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%else:
IMBNUM  ${2*dic['satnum']+2} ${mt.floor(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/
% endif