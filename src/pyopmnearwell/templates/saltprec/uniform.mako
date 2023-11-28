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
${dic['noCells'][0]} ${dic['noCells'][1]} ${dic['noCells'][2]} /
%else:
${max(dic['noCells'][0],dic['noCells'][1])} ${dic['noCells'][1]} ${dic['noCells'][2]} /
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
${(dic["hysteresis"]+1)*(dic['satnum']+dic['perforations'][0])} 1* 10000 /

% if dic["hysteresis"] ==1:
SATOPTS
 HYSTER  /
% endif

WELLDIMS
${dic['noCells'][2]} ${dic['noCells'][2]} 1 ${dic['noCells'][2]} /

UNIFIN
UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INCLUDE
  'GEOLOGY.INC' /
% if dic["pvMult"] > 0:
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

% if dic["hysteresis"] ==1:
EHYSTR
  1  3  2* BOTH /
% endif

SALTSOL
	${dic['salt_props'][1]} ${dic['salt_props'][2]}/
/

INCLUDE
'PERMFACT.INC' /
----------------------------------------------------------------------------
REGIONS
----------------------------------------------------------------------------
INCLUDE
  'REGIONS.INC' /
----------------------------------------------------------------------------
SOLUTION
---------------------------------------------------------------------------
EQUIL
 0 ${dic['pressure']} ${mt.floor(dic["initialphase"]*dic['dims'][2])} 0 0 0 1 1 0 /

SALTVD
0   ${dic['salt_props'][0]}
${dic['dims'][2]} ${dic['salt_props'][0]} /

RTEMPVD
0   ${dic['temperature']}
${dic['dims'][2]} ${dic['temperature']} /

RPTRST 
 'BASIC=2' FLOWS FLORES DEN VISC /
----------------------------------------------------------------------------
SUMMARY
----------------------------------------------------------------------------
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
RPTRST
 'BASIC=2' FLOWS FLORES DEN VISC /

WELSPECS
% if dic['grid'] == 'core':
'INJ0' 'G1' 1 ${1+mt.floor(dic['noCells'][2]/2)} 1* ${'GAS' if dic['inj'][0][3] > 0 else 'WATER'} 3* ${'NO' if dic["xflow"] > 0 else ''} /
% else:
% for i in range(dic['noCells'][2]):
'INJ${i}' 'G1' ${max(1, 1+mt.floor(dic['noCells'][1]/2))} ${max(1, 1+mt.floor(dic['noCells'][1]/2))} 1* ${'GAS' if dic['inj'][0][3] > 0 else 'WATER'} 3* ${'NO' if dic["xflow"] > 0 else ''} /
% endfor
% endif
% if dic["pvMult"] == 0 or dic['grid']== 'core':
% if dic['grid']== 'core':
'PRO0' 'G1'	${dic['noCells'][0]} ${1+mt.floor(dic['noCells'][2]/2)}	1* 'WATER' /
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'tensor3d' and dic['grid'] != 'coord3d' and dic['grid'] != 'cpg3d':
'PRO0' 'G1' ${dic['noCells'][0]} 1 1* 'WATER' /
% else:
'PRO0' 'G1' 1 1 1* 'WATER' /
'PRO1' 'G1' ${dic['noCells'][0]} 1 1* 'WATER' /
'PRO2' 'G1' 1 ${dic['noCells'][0]} 1* 'WATER' /
'PRO3' 'G1' ${dic['noCells'][0]}  ${dic['noCells'][0]} 1* 'WATER' /
% endif
% endif
/
COMPDAT
% if dic["jfactor"] == 0:
% if dic['grid'] == 'core':
'INJ0' 1 ${1+mt.floor(dic['noCells'][2]/2)} ${1+mt.floor(dic['noCells'][2]/2)} ${1+mt.floor(dic['noCells'][2]/2)} 'OPEN' 1* 1* ${dic['diameter']} /
% else:
% for i in range(dic['noCells'][2]):
'INJ${i}' ${max(1, 1+mt.floor(dic['noCells'][1]/2))} ${max(1, 1+mt.floor(dic['noCells'][1]/2))} ${i+1} ${i+1} 'OPEN' 1* 1* ${dic['diameter']} /
% endfor
% endif
% else:
% if dic['grid'] == 'core':
'INJ0' 1 ${1+mt.floor(dic['noCells'][2]/2)} ${1+mt.floor(dic['noCells'][2]/2)} ${1+mt.floor(dic['noCells'][2]/2)} 'OPEN' 1* ${dic["jfactor"]} /
% else:
% for i in range(dic['noCells'][2]):
'INJ${i}' ${max(1, 1+mt.floor(dic['noCells'][1]/2))} ${max(1, 1+mt.floor(dic['noCells'][1]/2))} ${i+1} ${i+1} 'OPEN' 1* ${dic["jfactor"]*2*mt.pi*dic['rock'][int(dic["layers"][i])][0]*dic['dims'][2]/dic['noCells'][2]} /
% endfor
% endif
% endif
% if dic["pvMult"] == 0 or dic['grid']== 'core':
% if dic['grid']== 'core':
'PRO0' ${dic['noCells'][0]} ${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)} ${1+mt.floor(dic['noCells'][2]/2)}	'OPEN' 1*	${dic["jfactor"]} /
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'tensor3d' and dic['grid'] != 'coord3d' and dic['grid'] != 'cpg3d':
'PRO0' ${dic['noCells'][0]}  1 1 ${0*dic['noCells'][2]+1}  'OPEN' 1* 1*  ${dic['diameter']} /
%else:
'PRO0' 1 1 1 ${0*dic['noCells'][2]+1} 'OPEN' 1* 1*  ${dic['diameter']} /
'PRO1' ${dic['noCells'][0]} 1 1 ${0*dic['noCells'][2]+1} 'OPEN' 1* 1*  ${dic['diameter']} /
'PRO2' 1 ${dic['noCells'][0]} 1 ${0*dic['noCells'][2]+1} 'OPEN' 1* 1*  ${dic['diameter']} /
'PRO3' ${dic['noCells'][0]} ${dic['noCells'][0]} 1 ${0*dic['noCells'][2]+1}  'OPEN' 1* 1*  ${dic['diameter']} /
% endif
% endif
/
% for j in range(len(dic['inj'])):
TUNING
1e-2 ${dic['inj'][j][2]} 1e-10 2* 1e-12/
/
/
WCONINJE
% for i in range(dic['noCells'][2]):
% if dic['inj'][j][3] > 0:
'INJ${i}' 'GAS' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4] / (dic['noCells'][2]*1.86843) : E}"}  1* 400/
% else:
'INJ${i}' 'WATER' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4] / (dic['noCells'][2]*998.108) : E}"}  1* 400/
%endif
%endfor
/
% if dic["pvMult"] == 0 or dic['grid']== 'core': 
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