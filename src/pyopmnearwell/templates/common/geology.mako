<%
import math as mt
%>\
% if dic['grid']=='cartesian2d':
INCLUDE
${dic['dx_file']} /

DY
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['dims'][1]/dic['nocells'][1]} /

DZ
% if dic["homo"]:
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['dims'][2]/dic['nocells'][2]} /
% else:
% for i in range(dic['satnum']):
${dic['nocells'][0]*dic['nocells'][1]*dic['rock'][i][4]}*${dic['rock'][i][3]/(dic['rock'][i][4])} ${'/' if loop.last else ''}\
% endfor
% endif

TOPS
${dic['nocells'][0]*dic['nocells'][1]}*0 /
% elif dic['grid']=='core':
DX
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['dims'][0]/dic['nocells'][0]} /

DY
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['dims'][2]/dic['nocells'][2]} /

DZ
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['dims'][2]/dic['nocells'][2]} /

TOPS
${dic['nocells'][0]*dic['nocells'][1]}*0 /
% elif dic['grid']=='radial':
INRAD
${dic["diameter"]} /

INCLUDE
${dic['drv_file']} /

DTHETAV
${dic['dims'][1]} /

DZ
% if dic["homo"]:
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['dims'][2]/dic['nocells'][2]} /
% else:
% for i in range(dic['satnum']):
${dic['nocells'][0]*dic['nocells'][1]*dic['rock'][i][4]}*${dic['rock'][i][3]/(dic['rock'][i][4])} ${'/' if loop.last else ''}\
% endfor
% endif

TOPS
${dic['nocells'][0]}*0 /
% elif dic['grid']=='cake' or dic['grid']=='tensor2d' or dic['grid']=='coord2d':
INCLUDE
${dic['grid_file']} /
% elif dic['grid']=='cpg3d':
INCLUDE
${dic['grid_file']} /
% else:
INCLUDE
${dic['dx_file']} /

INCLUDE
${dic['dy_file']} /

DZ
% if dic["homo"]:
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['dims'][2]/dic['nocells'][2]} /
% else:
% for i in range(dic['satnum']):
${dic['nocells'][0]*dic['nocells'][1]*dic['rock'][i][4]}*${dic['rock'][i][3]/(dic['rock'][i][4])} ${'/' if loop.last else ''}\
% endfor
% endif

TOPS
${dic['nocells'][0]*dic['nocells'][0]}*0 /
% endif  

% if dic["fluxnum"]:
EQUALREG
% for j, name in zip([0,0,1,2], ["PERMX", "PERMY", "PERMZ", "PORO "]):
% for i, rock in enumerate(dic['rock']):
${name} ${"".join([' ' for _ in range(dic["whsp"]-len(str(rock[j])))])}${rock[j]} ${i+1} F /
% endfor
% endfor
/
% else:
PERMX
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['rock'][0][0]} /

COPY 
PERMX PERMY /
/

PERMZ
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['rock'][0][1]} /

PORO
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*${dic['rock'][0][2]} /
% endif