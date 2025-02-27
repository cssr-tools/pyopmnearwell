-- Copyright (C) 2023 NORCE

% if dic['grid']== 'core':
BOX
1* 1* 1* 1* 1* 1* / 
MULTPV
%for mult in dic["coregeometry"]:
${mult} 
%endfor
/
ENDBOX
% elif dic["template"] in ["hwell", "hwellnoise"]:
BOX
1* 1* 1* 1* ${dic['nocells'][2]} ${dic['nocells'][2]} /  
MULTPV
${dic['nocells'][0]}*${dic["pvmult"]} /
ENDBOX
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'cpg3d' and dic['grid'] != 'tensor3d'  and dic['grid'] != 'coord3d':
BOX
${dic['nocells'][0]} ${dic['nocells'][0]} 1 1 1* 1* / 
MULTPV
${dic['nocells'][2]}*${dic["pvmult"]/(dic['xcor'][-1]-dic['xcor'][-2])} /
ENDBOX
% else:
BOX
1 1 1 ${dic['nocells'][0]} 1* 1* / 
MULTPV
% for _ in range(dic['nocells'][2]):
% for i in range(dic['nocells'][0]):
${'\t\t{0:.15e}'.format(dic["pvmult"]/(dic['xcorc'][i+1]-dic['xcorc'][i])) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX

BOX
1 ${dic['nocells'][0]} 1 1 1* 1* / 
MULTPV
% for _ in range(dic['nocells'][2]):
% for i in range(dic['nocells'][0]):
${'\t\t{0:.15e}'.format(dic["pvmult"]/(dic['xcorc'][i+1]-dic['xcorc'][i])) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX

BOX
${dic['nocells'][1]} ${dic['nocells'][1]} 1 ${dic['nocells'][0]} 1* 1* / 
MULTPV
% for _ in range(dic['nocells'][2]):
% for i in range(dic['nocells'][0]):
${'\t\t{0:.15e}'.format(dic["pvmult"]/(dic['xcorc'][i+1]-dic['xcorc'][i])) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX

BOX
1 ${dic['nocells'][0]} ${dic['nocells'][1]} ${dic['nocells'][1]} 1* 1* / 
MULTPV
% for _ in range(dic['nocells'][2]):
% for i in range(dic['nocells'][0]):
${'\t\t{0:.15e}'.format(dic["pvmult"]/(dic['xcorc'][i+1]-dic['xcorc'][i])) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX
%endif