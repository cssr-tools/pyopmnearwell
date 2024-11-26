<%
import math as mt
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

OIL
GAS
--DISGAS
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
${(dic["hysteresis"]+1)*(dic['satnum']+dic['perforations'][0])} 1* 10000 /

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
% if dic['write'] == 1:
INIT
% else:
GRIDFILE                               
0 0 /
% endif
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
----------------------------------------------------------------------------
REGIONS
----------------------------------------------------------------------------
INCLUDE
  'REGIONS.INC' /
----------------------------------------------------------------------------
SOLUTION
---------------------------------------------------------------------------
EQUIL
0 ${dic['pressure']} ${mt.floor((1-dic["initialphase"])*dic['dims'][2])} 0 0 0 1 1 0 /

RTEMPVD
0   ${dic['temperature']}
${dic['dims'][2]} ${dic['temperature']} /

RSVD
0   0.0
${dic['dims'][2]} 0.0 /

RS
${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*0.0 /
% if dic['write'] == 1:
RPTRST 
 'BASIC=2' FLOWS FLORES DEN VISC /
% endif
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

WPI
/
----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
% if dic['write'] == 1:
RPTRST
 'BASIC=2' FLOWS FLORES DEN VISC /
% endif

WELSPECS
%if dic['grid'] == 'core':
'INJ0'	'G1'	1 ${1+mt.floor(dic['noCells'][2]/2)}	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
'PRO0'	'G1'	1 ${1+mt.floor(dic['noCells'][2]/2)}	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
%else:
'INJ0'	'G1'	${max(1, 1+mt.floor(dic['noCells'][1]/2))} ${max(1, 1+mt.floor(dic['noCells'][1]/2))}	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
'PRO0'	'G1'	${max(1, 1+mt.floor(dic['noCells'][1]/2))} ${max(1, 1+mt.floor(dic['noCells'][1]/2))}	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
%endif
% if dic["pvMult"] == 0 or dic['grid']== 'core':
%if dic['grid']== 'core':
'PRO1'	'G1'	${dic['noCells'][0]}	${1+mt.floor(dic['noCells'][2]/2)}	1*	'GAS' 2* 'STOP' /
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'tensor3d' and dic['grid'] != 'coord3d' and dic['grid'] != 'cpg3d':
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
'INJ0'	${max(1, 1+mt.floor(dic['noCells'][1]/2))}	${max(1, 1+mt.floor(dic['noCells'][1]/2))}	1	${0*dic['noCells'][2]+1}	'OPEN'	1*	1*	${dic['diameter']} /
'PRO0'	${max(1, 1+mt.floor(dic['noCells'][1]/2))} ${max(1, 1+mt.floor(dic['noCells'][1]/2))}	1	${0*dic['noCells'][2]+1}	'OPEN' 1*	1*	${dic['diameter']} /
% else:
%if dic['grid'] == 'core':
'INJ0'	1	${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	'OPEN' 1*	${dic["jfactor"]}	 /
'PRO0'	1 ${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	'OPEN' 1*	${dic["jfactor"]} /
%else:
'INJ0'	${max(1, 1+mt.floor(dic['noCells'][1]/2))}	${max(1, 1+mt.floor(dic['noCells'][1]/2))}	1	${0*dic['noCells'][2]+1}	'OPEN'	1*	${dic["jfactor"]}	 /
'PRO0'	${max(1, 1+mt.floor(dic['noCells'][1]/2))} ${max(1, 1+mt.floor(dic['noCells'][1]/2))}	1	${0*dic['noCells'][2]+1}	'OPEN' 1*	${dic["jfactor"]} /
%endif
%endif
% if dic["pvMult"] == 0 or dic['grid']== 'core':
% if dic['grid']== 'core':
'PRO1'	${dic['noCells'][0]}	${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	'OPEN' 1*	${dic["jfactor"]} /
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'tensor3d' and dic['grid'] != 'coord3d' and dic['grid'] != 'cpg3d':
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
'RATE' ${f"{dic['inj'][j][4] / 998.108 : E}"}  1* 400/
%endif
/
WCONPROD
'PRO0' ${'OPEN' if dic['inj'][j][4] < 0 else 'SHUT'} 'GRAT' 2* ${f"{abs(dic['inj'][j][4]) / 0.0850397 : E}"} 2* ${dic["minWBHP_prod"][j] if dic['inj'][j][4] < 0 else ''}/
% if dic['grid'] == 'core':
'PRO1' 'OPEN' 'BHP' 5* ${dic['pressure']}/
%endif
% if dic["pvMult"] == 0:
% if dic['grid'] == 'cartesian' or dic['grid'] == 'tensor3d' or dic['grid'] == 'coord3d' or dic['grid'] == 'cpg3d':
'PRO1' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
'PRO2' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
'PRO3' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
'PRO4' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'} 'BHP' 5* ${dic['pressure']}/
%endif
%endif
/
WECON
'PRO0' 1* ${f"{dic['econ']*abs(dic['inj'][j][4]) / 0.0850397 : E}"} /
/
TSTEP
${mt.floor(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor