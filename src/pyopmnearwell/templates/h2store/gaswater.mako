<%
import math as mt
%>
-- Copyright (C) 2025 NORCE
----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
${dic['nocells'][0]} ${dic['nocells'][1]} ${dic['nocells'][2]} /

WATER
GAS
H2STORE
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

% if dic["hysteresis"] ==1:
EHYSTR
  1  ${dic["hyst_model"]}  2* KR /
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

% if dic['write'] == 1:
RPTRST 
 'BASIC=2' DEN VISC FLOWS /
% endif
----------------------------------------------------------------------------
SUMMARY
----------------------------------------------------------------------------
PERFORMA
FGMIP
FGMIT
FGMPT
FGIP
FWIP

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

FGMIR

FGMPR

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
 'BASIC=2' DEN VISC FLOWS /
% endif

WELSPECS
'INJ0'	'G1'	1 ${1+mt.floor(dic['nocells'][2]/2)}	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
'PRO0'	'G1'	1 ${1+mt.floor(dic['nocells'][2]/2)}	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
/
COMPDAT
'INJ0'	1	${1+mt.floor(dic['nocells'][1]/2)}	${1+mt.floor(dic['nocells'][1]/2)}	${1+mt.floor(dic['nocells'][2]/2)}	'OPEN' 1*	${dic["confact"]}	 /
'PRO0'	1   ${1+mt.floor(dic['nocells'][1]/2)}	${1+mt.floor(dic['nocells'][1]/2)}	${1+mt.floor(dic['nocells'][2]/2)}	'OPEN' 1*	${dic["confact"]} /
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
/
WECON
'PRO0' 1* ${f"{dic['econ']*abs(dic['inj'][j][4]) / 0.0850397 : E}"} /
/
TSTEP
${mt.floor(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor