<%
import math as mt
import numpy as np
rng = np.random.default_rng(7)
noise = rng.random(dic['noCells'][0]*dic['noCells'][2])
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
DISGAS
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
6 ${dic['noCells'][0]} 6 6 /

UNIFIN
UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INCLUDE
  'GEOLOGY.INC' /
OPERATE
% for k in range(dic['noCells'][2]-2):
% for i in range(dic['noCells'][0]):
PORO ${i+1} ${i+1} 1* 1* ${k+2} ${k+2} MULTX PORO ${max(0.2,min(0.8,noise[mt.floor(i/3)+mt.floor((k+2)/2)*dic['noCells'][0]]))} /
PERMZ ${i+1} ${i+1} 1* 1* ${k+2} ${k+2} MULTX PERMZ ${max(0.2,min(0.8,noise[mt.floor(i/3)+mt.floor((k+2)/2)*dic['noCells'][0]]))} /
% endfor
% endfor
/
% if dic["pvMult"] != 0:
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
0 ${dic['pressure']} ${mt.floor((1-dic["initialphase"])*dic['dims'][2])} 0 0 0 1 1 0 /

RTEMPVD
0   ${dic['temperature']}
${dic['dims'][2]} ${dic['temperature']} /

RSVD
0   0.0
${dic['dims'][2]} 0.0 /

RS
${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*0.0 /

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

WPI
/
----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
RPTRST
 'BASIC=2' FLOWS FLORES DEN VISC /

WELSPECS
'INJ0'	'G1' 1 1	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
'PRO0'	'G1' 1 1	1*	'GAS' 2* 'STOP' ${'NO' if dic["xflow"] > 0 else ''} /
/
COMPDAT
% for i in range(dic['noCells'][0]):
'INJ0' ${1+i} 1 1 1 'OPEN' 1* ${f"1* {dic['diameter']}" if dic["jfactor"] == 0 else dic["jfactor"]} /
% endfor
% for i in range(dic['noCells'][0]):
'PRO0' ${1+i} 1 1 1 'OPEN' 1* ${f"1* {dic['diameter']}" if dic["jfactor"] == 0 else dic["jfactor"]} /
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
'INJ0' 'OIL' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4] / 998.108 : E}"}  1* 400/
%endif
/
WCONPROD
'PRO0' ${'OPEN' if dic['inj'][j][4] < 0 else 'SHUT'} 'GRAT' 2* ${f"{abs(dic['inj'][j][4]) / 0.0850397 : E}"} 2* ${dic["minWBHP_prod"][j] if dic['inj'][j][4] < 0 else ''}/
/
WECON
'PRO0' 1* ${f"{dic['econ']*abs(dic['inj'][j][4]) / 0.0850397 : E}"} /
/
TSTEP
${mt.floor(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor