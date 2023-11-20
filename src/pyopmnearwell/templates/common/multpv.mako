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
1* 1* 1* 1* ${dic['noCells'][2]} ${dic['noCells'][2]} /  
MULTPV
${dic['noCells'][0]}*${dic["pvMult"]} /
ENDBOX
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'cpg3d' and dic['grid'] != 'tensor3d'  and dic['grid'] != 'coord3d':
BOX
${dic['noCells'][0]} ${dic['noCells'][0]} 1 1 1* 1* / 
MULTPV
${dic['noCells'][2]}*${dic["pvMult"]/(dic['xcor'][-1]-dic['xcor'][-2])} /
ENDBOX
% else:
BOX
1 1 1 ${dic['noCells'][0]} 1* 1* / 
MULTPV
% for _ in range(dic['noCells'][2]):
% for i in range(dic['noCells'][0]):
${'\t\t{0:.15e}'.format(dic["pvMult"]/(dic['xcorc'][i+1]-dic['xcorc'][i])) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX

BOX
1 ${dic['noCells'][0]} 1 1 1* 1* / 
MULTPV
% for _ in range(dic['noCells'][2]):
% for i in range(dic['noCells'][0]):
${'\t\t{0:.15e}'.format(dic["pvMult"]/(dic['xcorc'][i+1]-dic['xcorc'][i])) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX

BOX
${dic['noCells'][1]} ${dic['noCells'][1]} 1 ${dic['noCells'][0]} 1* 1* / 
MULTPV
% for _ in range(dic['noCells'][2]):
% for i in range(dic['noCells'][0]):
${'\t\t{0:.15e}'.format(dic["pvMult"]/(dic['xcorc'][i+1]-dic['xcorc'][i])) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX

BOX
1 ${dic['noCells'][0]} ${dic['noCells'][1]} ${dic['noCells'][1]} 1* 1* / 
MULTPV
% for _ in range(dic['noCells'][2]):
% for i in range(dic['noCells'][0]):
${'\t\t{0:.15e}'.format(dic["pvMult"]/(dic['xcorc'][i+1]-dic['xcorc'][i])) }\
% endfor
${'/\n' if loop.last else ' '}\
% endfor
ENDBOX
%endif