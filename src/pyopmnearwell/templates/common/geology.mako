<%
import math as mt
%>
-- Copyright (C) 2023 NORCE

% if dic['grid']== 'cartesian2d':
INCLUDE
${dic['dx_file']} /
DY 
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['dims'][1]/dic['nocells'][1]} /
DZ 
%for i in range(dic['satnum']):
${dic['nocells'][0]*dic['nocells'][1]*dic['rock'][i][4]}*${dic['rock'][i][3]/(dic['rock'][i][4])}
%endfor
/
TOPS
${dic['nocells'][0]*dic['nocells'][1]}*0. /
% elif dic['grid']=='core':
DX 
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['dims'][0]/dic['nocells'][0]} /
DY 
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['dims'][2]/dic['nocells'][2]} /
DZ 
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['dims'][2]/dic['nocells'][2]} /
TOPS
${dic['nocells'][0]*dic['nocells'][1]}*0. /
% elif dic['grid']=='radial':
INRAD
${dic["diameter"]}
/
INCLUDE
${dic['drv_file']} /
DTHETAV
${dic['dims'][1]} /
DZ 
%for i in range(dic['satnum']):
${dic['nocells'][0]*dic['nocells'][1]*dic['rock'][i][4]}*${dic['rock'][i][3]/(dic['rock'][i][4])}
%endfor
/
TOPS
${dic['nocells'][0]}*0. /
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
%for i in range(dic['satnum']):
${dic['nocells'][0]*dic['nocells'][1]*dic['rock'][i][4]}*${dic['rock'][i][3]/(dic['rock'][i][4])}
%endfor
/
TOPS
${dic['nocells'][0]*dic['nocells'][0]}*0. /
%endif  

EQUALS
% for i in range(dic['nocells'][2]):
PERMX  ${dic['rock'][int(dic["layers"][i])][0]} 4* ${i+1} ${i+1} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] not in ['cartesian','cpg3d','coord3d','tensor3d']:
PERMX  ${dic['rock'][dic['satnum']][0]} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 2* ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
%else:
PERMX  ${dic['rock'][dic['satnum']][0]} ${mt.ceil(dic["nocells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/

EQUALS
% for i in range(dic['nocells'][2]):
PERMZ  ${dic['rock'][int(dic["layers"][i])][1]} 4* ${i+1} ${i+1} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] not in ['cartesian','cpg3d','coord3d','tensor3d']:
PERMZ ${dic['rock'][dic['satnum']][1]} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 2* ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
%else:
PERMZ ${dic['rock'][dic['satnum']][1]} ${mt.ceil(dic["nocells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/

COPY 
PERMX PERMY /
/

EQUALS
% for i in range(dic['nocells'][2]):
PORO ${dic['rock'][int(dic["layers"][i])][2]} 4* ${i+1} ${i+1} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] not in ['cartesian','cpg3d','coord3d','tensor3d']:
PORO ${dic['rock'][dic['satnum']][2]} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 2* ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
%else:
PORO ${dic['rock'][dic['satnum']][2]} ${mt.ceil(dic["nocells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${mt.ceil(dic["nocells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} ${(i+1)*mt.floor(dic['nocells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/