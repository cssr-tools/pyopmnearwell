<%
import math as mt
%>
-- Copyright (C) 2024 NORCE
----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
${dic['nocells'][0]} ${dic['nocells'][1]} ${dic['nocells'][2]} /

WATER
GAS
H2STORE
DISGASW
BIOFILM

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

PERMFACT
-- PORO PERM
-- FACTOR FACTOR
0.000000E+00 8.955002E-04
3.500000E-01 8.955002E-04
4.222222E-01 2.710162E-02
4.944444E-01 8.009931E-02
5.666667E-01 1.556337E-01
6.388889E-01 2.515992E-01
7.111111E-01 3.666193E-01
7.833333E-01 4.996865E-01
8.555556E-01 6.500148E-01
9.277778E-01 8.169646E-01
1.000000E+00 1.000000E+00 /

BIOFPARA
-- BDEN DEATH GROWTH HALF YIELD FACTOR ATACH DETRAT DETEXP UREA HALF CDEN YUTOC
% for i in range(dic["satnum"]):
${dic['biof'][int(dic["layers"][i])][0]} ${dic['biof'][int(dic["layers"][i])][1]} ${dic['biof'][int(dic["layers"][i])][2]} ${dic['biof'][int(dic["layers"][i])][3]} ${dic['biof'][int(dic["layers"][i])][4]} 1 ${dic['biof'][int(dic["layers"][i])][5]} ${dic['biof'][int(dic["layers"][i])][6]} ${dic['biof'][int(dic["layers"][i])][7]} 4*  /
% endfor
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
 'BASIC=2' DEN VISC /
% endif

EQUALS
% for i in range(dic['nocells'][2]):
SBIOF  0 1 19 2* ${i+1} ${i+1} /
SBIOF  ${dic['biof'][int(dic["layers"][i])][8]} 20 80 2* ${i+1} ${i+1} /
SBIOF  0 81 100 2* ${i+1} ${i+1} /
--SBIOF  ${dic['biof'][int(dic["layers"][i])][8]} 1 80 2* ${i+1} ${i+1} /
--SBIOF  0 81 100 2* ${i+1} ${i+1} /
% endfor
/
----------------------------------------------------------------------------
SUMMARY
----------------------------------------------------------------------------
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