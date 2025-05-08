<%
import math as mt
import numpy as np
%>
-- Copyright (C) 2023 NORCE
----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
%if dic['grid']== 'core':
${dic['nocells'][0]} ${dic['nocells'][1]} ${dic['nocells'][2]} /
%else:
${max(dic['nocells'][0],dic['nocells'][1])} ${dic['nocells'][1]} ${dic['nocells'][2]} /
%endif

WATER
GAS
BRINE
PRECSALT
VAPWAT
CO2STORE
DISGASW

METRIC

START
1 'JAN' 2000 /

%if dic['grid']== 'radial':
RADIAL
%endif

EQLDIMS
/

TABDIMS
${(1*(dic["hysteresis"]!=0)+1)*(dic['satnum']+dic['perforations'][0])} /

% if dic["hysteresis"]!=0:
SATOPTS
HYSTER  /
% endif

WELLDIMS
${dic['nocells'][2]} ${dic['nocells'][2]} 1 ${dic['nocells'][2]} /

UNIFIN
UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
% if dic['write'] == 1:
INIT
% else:
GRIDFILE 
0 0 /
% endif
INCLUDE
'GEOLOGY.INC' /
% if dic["pvmult"] > 0:
----------------------------------------------------------------------------
EDIT
----------------------------------------------------------------------------
INCLUDE
'MULTPV.INC' /
%endif
----------------------------------------------------------------------------
PROPS
----------------------------------------------------------------------------
INCLUDE
'TABLES.INC' /

% if dic["hysteresis"]!=0:
EHYSTR
1* ${0 if dic["hysteresis"].upper()=="CARLSON" else 2} 2* BOTH /
% endif

SALTSOL
${dic['saltprops'][1]} ${dic['saltprops'][2]}/
/

% if dic["rockcomp"] > 0:
ROCK
276.0 ${dic["rockcomp"]} /
% endif

INCLUDE
'PERMFACT.INC' /

% if dic["pcfact"] > 0:
INCLUDE
'PCFACT.INC' /
% endif
----------------------------------------------------------------------------
REGIONS
----------------------------------------------------------------------------
INCLUDE
'REGIONS.INC' /
----------------------------------------------------------------------------
SOLUTION
----------------------------------------------------------------------------
EQUIL
0 ${dic['pressure']} ${mt.floor(dic["initialphase"]*dic['dims'][2])} 0 0 0 1 1 0 /

SALTVD
0   ${dic['saltprops'][0]}
${dic['dims'][2]} ${dic['saltprops'][0]} /

RTEMPVD
0   ${dic['temperature'][0]}
${dic['dims'][2]} ${dic['temperature'][1]} /
% if dic['write'] == 1:
RPTRST 
'BASIC=2' DEN VISC PCOW PCOG /
% endif
----------------------------------------------------------------------------
SUMMARY
----------------------------------------------------------------------------
PERFORMA
FPR 

FGIP

FWIP

FGIR

FWIR

FGIT

FWIT

WPI
/

FWCD

WGIR
/

WGIT
/

WBHP
/

RPR
/

RWIP
/

RGIP
/
----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
% if dic['write'] == 1:
RPTRST
'BASIC=2' DEN VISC PCOW PCOG /
% endif

WELSPECS
% if dic['grid'] == 'core':
'INJ0' 'G1' 1 ${1+mt.floor(dic['nocells'][2]/2)} 1* ${'GAS' if dic['inj'][0][3] > 0 else 'WATER'} 3* ${'NO' if dic["xflow"] > 0 else ''} /
% else:
% for i in range(dic['nocells'][2]):
'INJ${i}' 'G1' ${max(1, 1+mt.floor(dic['nocells'][1]/2))} ${max(1, 1+mt.floor(dic['nocells'][1]/2))} 1* ${'GAS' if dic['inj'][0][3] > 0 else 'WATER'} 3* ${'NO' if dic["xflow"] > 0 else ''} /
% endfor
% endif
% if dic["pvmult"] == 0 or dic['grid']== 'core':
% if dic['grid']== 'core':
'PRO0' 'G1'	${dic['nocells'][0]} ${1+mt.floor(dic['nocells'][2]/2)}	1* 'WATER' /
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'tensor3d' and dic['grid'] != 'coord3d' and dic['grid'] != 'cpg3d':
'PRO0' 'G1' ${dic['nocells'][0]} 1 1* 'WATER' /
% else:
'PRO0' 'G1' 1 1 1* 'WATER' /
'PRO1' 'G1' ${dic['nocells'][0]} 1 1* 'WATER' /
'PRO2' 'G1' 1 ${dic['nocells'][0]} 1* 'WATER' /
'PRO3' 'G1' ${dic['nocells'][0]}  ${dic['nocells'][0]} 1* 'WATER' /
% endif
% endif
/
COMPDAT
% if dic["confact"] == 0:
% if dic['grid'] == 'core':
'INJ0' 1 ${1+mt.floor(dic['nocells'][2]/2)} ${1+mt.floor(dic['nocells'][2]/2)} ${1+mt.floor(dic['nocells'][2]/2)} 'OPEN' 1* 1* ${dic['diameter']} /
% else:
% for i in range(dic['nocells'][2]):
'INJ${i}' ${max(1, 1+mt.floor(dic['nocells'][1]/2))} ${max(1, 1+mt.floor(dic['nocells'][1]/2))} ${i+1} ${i+1} 'OPEN' 1* 1* ${dic['diameter']} /
% endfor
% endif
% else:
% if dic['grid'] == 'core':
'INJ0' 1 ${1+mt.floor(dic['nocells'][2]/2)} ${1+mt.floor(dic['nocells'][2]/2)} ${1+mt.floor(dic['nocells'][2]/2)} 'OPEN' 1* ${dic["confact"]} /
% else:
% for i in range(dic['nocells'][2]):
'INJ${i}' ${max(1, 1+mt.floor(dic['nocells'][1]/2))} ${max(1, 1+mt.floor(dic['nocells'][1]/2))} ${i+1} ${i+1} 'OPEN' 1* ${dic["confact"]*2*mt.pi*dic['rock'][int(dic["layers"][i])][0]*dic['dims'][2]/dic['nocells'][2]} /
% endfor
% endif
% endif
% if dic["pvmult"] == 0 or dic['grid']== 'core':
% if dic['grid']== 'core':
'PRO0' ${dic['nocells'][0]} ${1+mt.floor(dic['nocells'][2]/2)}	${1+mt.floor(dic['nocells'][2]/2)} ${1+mt.floor(dic['nocells'][2]/2)}	'OPEN' 1*	${dic["confact"]} /
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'tensor3d' and dic['grid'] != 'coord3d' and dic['grid'] != 'cpg3d':
'PRO0' ${dic['nocells'][0]}  1 1 ${0*dic['nocells'][2]+1}  'OPEN' 1* 1*  ${dic['diameter']} /
%else:
'PRO0' 1 1 1 ${0*dic['nocells'][2]+1} 'OPEN' 1* 1*  ${dic['diameter']} /
'PRO1' ${dic['nocells'][0]} 1 1 ${0*dic['nocells'][2]+1} 'OPEN' 1* 1*  ${dic['diameter']} /
'PRO2' 1 ${dic['nocells'][0]} 1 ${0*dic['nocells'][2]+1} 'OPEN' 1* 1*  ${dic['diameter']} /
'PRO3' ${dic['nocells'][0]} ${dic['nocells'][0]} 1 ${0*dic['nocells'][2]+1}  'OPEN' 1* 1*  ${dic['diameter']} /
% endif
% endif
/
% for j in range(len(dic['inj'])):
TUNING
1e-2 ${dic['inj'][j][2]} 1e-10 2* 1e-12/
/
/
WCONINJE
% for i in range(dic['nocells'][2]):
% if dic['inj'][j][3] > 0:
'INJ${i}' 'GAS' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4] / (dic['nocells'][2]*1.86843) : E}"}  1* 400/
% else:
'INJ${i}' 'WATER' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4] / (dic['nocells'][2]*998.108) : E}"}  1* 400/
%endif
%endfor
/
% if dic["pvmult"] == 0 or dic['grid']== 'core': 
WCONPROD
% if dic['grid'] == 'cartesian' or dic['grid'] == 'tensor3d' or dic['grid'] == 'coord3d' or dic['grid'] == 'cpg3d':
'PRO0' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
'PRO1' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
'PRO2' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
'PRO3' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
% else:
'PRO0' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
%endif
/
%endif
TSTEP
${mt.floor(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor