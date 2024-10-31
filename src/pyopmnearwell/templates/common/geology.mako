<%
import math as mt
%>
-- Copyright (C) 2023 NORCE

% if dic['grid']== 'cartesian2d':
INCLUDE
${dic['dx_file']} /
DY 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dims'][1]/dic['noCells'][1]} /
DZ 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dims'][2]/dic['noCells'][2]} /
TOPS
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*0. /
% elif dic['grid']== 'core':
DX 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dims'][0]/dic['noCells'][0]} /
DY 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dims'][2]/dic['noCells'][2]} /
DZ 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dims'][2]/dic['noCells'][2]} /
TOPS
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*0. /
% elif dic['grid']== 'radial':
INRAD
${dic["diameter"]}
/
INCLUDE
  ${dic['drv_file']} /
DTHETAV
  ${dic['dims'][1]} /
DZ 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dims'][2]/dic['noCells'][2]} /
TOPS
  ${dic['noCells'][0]}*0. /
% elif dic['grid']== 'cake' or dic['grid']== 'tensor2d' or dic['grid']== 'coord2d':
INCLUDE
  ${dic['grid_file']} /
% elif dic['grid']== 'cpg3d':
INCLUDE
  ${dic['grid_file']} /
% else:
INCLUDE
${dic['dx_file']} /
INCLUDE
${dic['dy_file']} /
DZ 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dims'][2]/dic['noCells'][2]} /
TOPS
  ${dic['noCells'][0]*dic['noCells'][0]*dic['noCells'][2]}*0. /
%endif  

EQUALS
% for i in range(dic['noCells'][2]):
PERMX  ${dic['rock'][int(dic["layers"][i])][0]} 1* 1* 1* 1* ${i+1} ${i+1} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] != 'cartesian':
PERMX  ${dic['rock'][dic['satnum']][0]} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 1* 1* ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%else:
PERMX  ${dic['rock'][dic['satnum']][0]} ${mt.floor(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/

EQUALS
% for i in range(dic['noCells'][2]):
PERMZ  ${dic['rock'][int(dic["layers"][i])][1]} 1* 1* 1* 1* ${i+1} ${i+1} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] != 'cartesian':
PERMZ  ${dic['rock'][dic['satnum']][1]} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 1* 1* ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%else:
PERMZ  ${dic['rock'][dic['satnum']][1]} ${mt.floor(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/

COPY 
PERMX PERMY /
/

EQUALS
% for i in range(dic['noCells'][2]):
PORO  ${dic['rock'][int(dic["layers"][i])][2]} 1* 1* 1* 1* ${i+1} ${i+1} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] != 'cartesian':
PORO  ${dic['rock'][dic['satnum']][2]} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 1* 1* ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%else:
PORO  ${dic['rock'][dic['satnum']][2]} ${mt.floor(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.floor(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/