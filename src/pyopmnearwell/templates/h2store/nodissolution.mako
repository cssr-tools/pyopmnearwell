<%
import math as mt
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
--DISGASW
H2STORE

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
6 ${dic['nocells'][2]} 6 6 /

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

RTEMPVD
0   ${dic['temperature'][0]}
${dic['dims'][2]} ${dic['temperature'][1]} /

RVW
${dic['nocells'][0]*dic['nocells'][1]*dic['nocells'][2]}*0.0 /
% if dic['write'] == 1:
RPTRST 
 'BASIC=2' DEN VISC /
% endif
----------------------------------------------------------------------------
SUMMARY
-------------------------------------------------------------------------
PERFORMA---
CGIR
 INJ0 /
 PRO0 /
/

CGIRL
 INJ0 /
 PRO0 /
/

WGIRL
% for j in range(0*dic['nocells'][2]+1):
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
% for j in range(0*dic['nocells'][2]+1):
 'INJ0'  ${j+1}  /
 'PRO0'  ${j+1}  /
% endfor
/

FPR 

FGIP

FWIP

FGIR

FWIR

FGIT

FGPT

FWIT

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

RWIP
/

RGIP
/

WWPR
/

WPI
/
----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
% if dic['write'] == 1:
RPTRST
 'BASIC=2' DEN VISC /
% endif

WELSPECS
%if dic['grid'] == 'core':
'INJ0'	'G1'	1 ${1+mt.floor(dic['nocells'][2]/2)}	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
'PRO0'	'G1'	1 ${1+mt.floor(dic['nocells'][2]/2)}	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
%else:
'INJ0'	'G1'	${max(1, 1+mt.floor(dic['nocells'][1]/2))} ${max(1, 1+mt.floor(dic['nocells'][1]/2))}	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
'PRO0'	'G1'	${max(1, 1+mt.floor(dic['nocells'][1]/2))} ${max(1, 1+mt.floor(dic['nocells'][1]/2))}	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
%endif
% if dic["pvmult"] == 0 or dic['grid']== 'core':
%if dic['grid']== 'core':
'PRO1'	'G1'	${dic['nocells'][0]}	${1+mt.floor(dic['nocells'][2]/2)}	1*	'GAS' 2* 'STOP' /
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'tensor3d' and dic['grid'] != 'coord3d' and dic['grid'] != 'cpg3d':
'PRO1'	'G1'	${dic['nocells'][0]}	1	1*	'GAS' /
%else:
'PRO1'	'G1'	1	1	1*	'WATER' /
'PRO2'	'G1'	${dic['nocells'][0]}	1	1*	'WATER' /
'PRO3'	'G1'	1	${dic['nocells'][0]}	1*	'WATER' /
'PRO4'	'G1'	${dic['nocells'][0]}	${dic['nocells'][0]}	1*	'WATER' /
% endif
% endif
/
COMPDAT
% if dic["confact"] == 0:
'INJ0'	${max(1, 1+mt.floor(dic['nocells'][1]/2))}	${max(1, 1+mt.floor(dic['nocells'][1]/2))}	1	${0*dic['nocells'][2]+1}	'OPEN'	1*	1*	${dic['diameter']} /
'PRO0'	${max(1, 1+mt.floor(dic['nocells'][1]/2))} ${max(1, 1+mt.floor(dic['nocells'][1]/2))}	1	${0*dic['nocells'][2]+1}	'OPEN' 1*	1*	${dic['diameter']} /
% else:
%if dic['grid'] == 'core':
'INJ0'	1	${1+mt.floor(dic['nocells'][2]/2)}	${1+mt.floor(dic['nocells'][2]/2)}	${1+mt.floor(dic['nocells'][2]/2)}	'OPEN' 1*	${dic["confact"]}	 /
'PRO0'	1 ${1+mt.floor(dic['nocells'][2]/2)}	${1+mt.floor(dic['nocells'][2]/2)}	${1+mt.floor(dic['nocells'][2]/2)}	'OPEN' 1*	${dic["confact"]} /
%else:
'INJ0'	${max(1, 1+mt.floor(dic['nocells'][1]/2))}	${max(1, 1+mt.floor(dic['nocells'][1]/2))}	1	${0*dic['nocells'][2]+1}	'OPEN'	1*	${dic["confact"]}	 /
'PRO0'	${max(1, 1+mt.floor(dic['nocells'][1]/2))} ${max(1, 1+mt.floor(dic['nocells'][1]/2))}	1	${0*dic['nocells'][2]+1}	'OPEN' 1*	${dic["confact"]} /
%endif
%endif
% if dic["pvmult"] == 0 or dic['grid']== 'core':
% if dic['grid']== 'core':
'PRO1'	${dic['nocells'][0]}	${1+mt.floor(dic['nocells'][2]/2)}	${1+mt.floor(dic['nocells'][2]/2)}	${1+mt.floor(dic['nocells'][2]/2)}	'OPEN' 1*	${dic["confact"]} /
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'tensor3d' and dic['grid'] != 'coord3d' and dic['grid'] != 'cpg3d':
'PRO1'	${dic['nocells'][0]}	1	1	${0*dic['nocells'][2]+1}	'OPEN' 1*	1*	${dic['diameter']} /
%else:
'PRO1'	1	1	1	${dic['nocells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
'PRO2'	${dic['nocells'][0]}	1	 1 ${dic['nocells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
'PRO3'	1	${dic['nocells'][0]} 1 ${dic['nocells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
'PRO4'	${dic['nocells'][0]}	${dic['nocells'][0]}	1	${dic['nocells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
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
'INJ0' 'WATER' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4] / 998.108 : E}"}  1* 400/
%endif
/
WCONPROD
'PRO0' ${'OPEN' if dic['inj'][j][4] < 0 else 'SHUT'} 'GRAT' 2* ${f"{abs(dic['inj'][j][4]) / 0.0850397 : E}"} 2* ${dic['inj'][j][5] if dic['inj'][j][4] < 0 else ''}/
% if dic['grid'] == 'core':
'PRO1' 'OPEN' 'BHP' 5* ${dic['pressure']}/
%endif
% if dic["pvmult"] == 0:
% if dic['grid'] == 'cartesian' or dic['grid'] == 'tensor3d' or dic['grid'] == 'coord3d' or dic['grid'] == 'cpg3d':
'PRO1' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
'PRO2' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
'PRO3' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
'PRO4' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
%endif
%endif
/
% if dic['econ']>0:
WECON
'PRO0' 1* ${f"{dic['econ']*abs(dic['inj'][j][4]) / 0.0850397 : E}"} /
/
% endif
TSTEP
${mt.floor(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor