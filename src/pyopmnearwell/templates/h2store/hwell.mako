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
DISGASW
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
${(1*(dic["hysteresis"]!=0)+1)*(dic['satnum']+dic['perforations'][0])} 1* 10000 /

% if dic["hysteresis"] !=0:
SATOPTS
 HYSTER  /
% endif

WELLDIMS
6 ${dic['nocells'][0]} 6 6 /

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
  1  ${0 if dic["hysteresis"].upper()=="CARLSON" else 2}  2* KR /
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
'INJ0'	'G1' 1 1	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
'PRO0'	'G1' 1 1	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
/
COMPDAT
% for i in range(dic['nocells'][0]):
'INJ0' ${1+i} 1 1 1 'OPEN' 1* ${f"1* {dic['diameter']}" if dic["confact"] == 0 else dic["confact"]} /
% endfor
% for i in range(dic['nocells'][0]):
'PRO0' ${1+i} 1 1 1 'OPEN' 1* ${f"1* {dic['diameter']}" if dic["confact"] == 0 else dic["confact"]} /
% endfor
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
% if dic['econ']>0:
WECON
'PRO0' 1* ${f"{dic['econ']*abs(dic['inj'][j][4]) / 0.0850397 : E}"} /
/
% endif
TSTEP
${mt.floor(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor