<%
import math as mt
%>
-- Copyright (C) 2023 NORCE

----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
${max(dic['noCells'][0],dic['noCells'][1])} ${dic['noCells'][1]} ${dic['noCells'][2]} /

%if dic['grid']== 'radial':
RADIAL
%endif

EQLDIMS
/

TABDIMS
${(dic["hysteresis"]+1)*(dic['satnum']+dic['perforations'][0])} 1* 10000 /

OIL
GAS
DISGAS
H2STORE

MICROBES

METRIC

START
1 'JAN' 2000 /

% if dic["hysteresis"] ==1:
SATOPTS
 HYSTER  /
% endif

WELLDIMS
6 ${dic['noCells'][2]} 6 6 /

UNIFIN
UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INIT

% if dic['grid']== 'cartesian2d':
INCLUDE
'${dic['exe']}/${dic['fol']}/preprocessing/DX.INC' /
DY 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dims'][1]/dic['noCells'][1]} /
DZ 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dims'][2]/dic['noCells'][2]} /
TOPS
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*0. /
% elif dic['grid']== 'radial':
INRAD
${dic["diameter"]}
/
INCLUDE
  '${dic['exe']}/${dic['fol']}/preprocessing/DRV.INC' /
DTHETAV
  ${dic['dims'][1]} /
DZ 
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['dims'][2]/dic['noCells'][2]} /
TOPS
  ${dic['noCells'][0]}*0. /
% elif dic['grid']== 'cake':
INCLUDE
  '${dic['exe']}/${dic['fol']}/preprocessing/CAKE.INC' /
% elif dic['grid']== 'cave':
INCLUDE
  '${dic['exe']}/${dic['fol']}/preprocessing/CAVE.INC' /
% else:
INCLUDE
'${dic['exe']}/${dic['fol']}/preprocessing/DX.INC' /
INCLUDE
'${dic['exe']}/${dic['fol']}/preprocessing/DY.INC' /
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

% if dic["pvMult"] != 0:
----------------------------------------------------------------------------
EDIT
----------------------------------------------------------------------------
% if dic['grid'] != 'cartesian' and dic['grid'] != 'cave':
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

%endif

----------------------------------------------------------------------------
PROPS
----------------------------------------------------------------------------

-- Microbe parameters
BACTPARA
--max. growth rate  half. vel. gas  yield coeff.  stoic. coeff.  decay coeff.
  2.246e-5          5.018e-8        5.6542255     -4             0.0 /

INCLUDE
'${dic['exe']}/${dic['fol']}/preprocessing/TABLES.INC' /

% if dic["hysteresis"] ==1:
EHYSTR
  1  3  2* BOTH /
% endif

----------------------------------------------------------------------------
REGIONS
----------------------------------------------------------------------------

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

----------------------------------------------------------------------------
SOLUTION
---------------------------------------------------------------------------
EQUIL
 0 ${dic['pressure']} ${mt.floor((1-dic["initialphase"])*dic['dims'][2])} 0 0 0 1 1 0 /
--PRESSURE
--% for i in range(dic['noCells'][2]):
--	${dic['noCells'][0]*dic['noCells'][1]}*${dic['pressure']+1e-5*i*0.6785064*9.81*dic['dims'][2]/dic['noCells'][2]}
--% endfor
--/
--SGAS
--	${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*0.0 /
RTEMPVD
0   ${dic['temperature']}
${dic['dims'][2]} ${dic['temperature']} /
RSVD
0   0.0
${dic['dims'][2]} 0.0 /
RS
${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*0.0 /

--PRESSURE
--  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['pressure']} /

--SOIL
--  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${1. - dic["initialphase"]} /

--SGAS
--  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic["initialphase"]} /

-- Initial microbe distribution
SBACT
  ${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*0.01 /

RPTRST 
 'BASIC=2' FLOWS FLORES DEN VISC /

----------------------------------------------------------------------------
SUMMARY
----------------------------------------------------------------------------

CGIR
 INJ0 /
 PRO0 /
/

CGIRL
 INJ0 /
 PRO0 /
/

WGIRL
% for j in range(0*dic['noCells'][2]+1):
 'INJ0'  ${j+1}  /
 'PRO0'  ${j+1}  /
% endfor
/

CGIT
 INJ0 /
 PRO0 /
/

CGITL
 INJ0 /
 PRO0 /
/

WGITL
% for j in range(0*dic['noCells'][2]+1):
 'INJ0'  ${j+1}  /
 'PRO0'  ${j+1}  /
% endfor
/

FPR 

FGIP

FOIP

FGIR

FOIR

FGIT

FGPT

FOIT

WGIR
/

WGPR
/

WGIT
/

WGPT
/

WBHP
/

RPR
/

ROIP
/

RGIP
/

WOPR
/


----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
RPTRST
 'BASIC=2' FLOWS FLORES DEN VISC /

WELSPECS
'INJ0'	'G1'	${max(1, mt.floor(dic['noCells'][1]/2))} ${max(1, mt.floor(dic['noCells'][1]/2))}	1*	'GAS' 2* 'STOP' /
'PRO0'	'G1'	${max(1, mt.floor(dic['noCells'][1]/2))} ${max(1, mt.floor(dic['noCells'][1]/2))}	1*	'GAS' 2* 'STOP'  /
% if dic["pvMult"] == 0:
% if dic['grid'] != 'cartesian' and dic['grid'] != 'cave':
'PRO1'	'G1'	${dic['noCells'][0]}	1	1*	'GAS' /
%else:
'PRO1'	'G1'	1	1	1*	'OIL' /
'PRO2'	'G1'	${dic['noCells'][0]}	1	1*	'OIL' /
'PRO3'	'G1'	1	${dic['noCells'][0]}	1*	'OIL' /
'PRO4'	'G1'	${dic['noCells'][0]}	${dic['noCells'][0]}	1*	'OIL' /
% endif
% endif
/
COMPDAT
% if dic["jfactor"] == 0:
'INJ0'	${max(1, mt.floor(dic['noCells'][1]/2))}	${max(1, mt.floor(dic['noCells'][1]/2))}	${1} ${1}	'OPEN'	1*	1*	${dic['diameter']} /
% else:
'INJ0'	${max(1, mt.floor(dic['noCells'][1]/2))}	${max(1, mt.floor(dic['noCells'][1]/2))}	${1} ${1}	'OPEN'	1*	${dic["jfactor"]}	 /
%endif
'PRO0'	${max(1, mt.floor(dic['noCells'][1]/2))} ${max(1, mt.floor(dic['noCells'][1]/2))}	${1} ${1}	'OPEN' 1*	1*	${dic['diameter']} /
% if dic["pvMult"] == 0:
% if dic['grid'] != 'cartesian':
'PRO1'	${dic['noCells'][0]}	1	1	${0*dic['noCells'][2]+1}	'OPEN' 1*	1*	${dic['diameter']} /
%else:
'PRO1'	1	1	1	${dic['noCells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
'PRO2'	${dic['noCells'][0]}	1	 1 ${dic['noCells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
'PRO3'	1	${dic['noCells'][0]} 1 ${dic['noCells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
'PRO4'	${dic['noCells'][0]}	${dic['noCells'][0]}	1	${dic['noCells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
% endif
% endif
/
% for j in range(len(dic['inj'])):
TUNING
1e-2 ${dic['inj'][j][2]} 1e-10 2* 1e-12/
/
/
WCONINJE
% if dic['inj'][j][3] > 0:
'INJ0' 'GAS' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4] / 0.0850397 : E}"}  1* 400/
% else:
'INJ0' 'OIL' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4] / 998.108 : E}"}  1* 400/ 998.108
%endif
/
WCONPROD
'PRO0' ${'OPEN' if dic['inj'][j][4] < 0 else 'SHUT'} 'GRAT' 2* ${f"{abs(dic['inj'][j][4]) / 0.0850397 : E}"} 2* ${.9*dic['pressure']}/
/
--WECON
--'PRO0' 1* ${f"{.95*abs(dic['inj'][j][4]) / 0.0850397 : E}"} /
--/
% if dic["pvMult"] == 0:
% if dic['grid'] == 'cartesian':
'PRO1' 'OPEN' 'BHP' 5* ${dic['pressure']}/
'PRO2' 'OPEN' 'BHP' 5* ${dic['pressure']}/
'PRO3' 'OPEN' 'BHP' 5* ${dic['pressure']}/
'PRO4' 'OPEN' 'BHP' 5* ${dic['pressure']}/
%endif
/
%endif
TSTEP
${mt.floor(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor