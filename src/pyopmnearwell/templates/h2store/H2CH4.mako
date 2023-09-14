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
VAPOIL
DIFFUSE

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
INCLUDE
  'GEOLOGY.INC' /
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
-- Diffusion coefficients for H2 and CH4 are 7.25995e-5 m2/s = 6.2726 m2/d
-- 1. The oil molecular weight
-- 2. The gas molecular weight
-- 3. The gas-in-gas diffusion coefficient
-- 4. The oil-in-gas diffusion coefficient

-- 1.     2.    3.   4.
DIFFC
  16.043 2.016 6.2726 6.2726  /

-- Standard temperature: 288.71 K, 15.56 °C
-- Standard pressure: 1.013250 bar

-- Fluid properties from CoolProp, doi/abs/10.1021/ie4033999
-- CH4 WATER H2
DENSITY
  0.6785064 999.70 0.0850397  /

ROCK
  40 4.3e-5  /

-- Methane as dead oil fluid type
-- Pressure[bar] FVF[-] Viscosity[cP]
PVDO
  39.95  0.0270783155  0.0126098701
  40.00  0.0270428829  0.01261087
  40.05  0.0270075391  0.0126118705
  40.10  0.0269722838  0.0126128714
/ 
--  Hydrogen as a wet gas fluid type
--  Pressure[bar] RV[-] FVF[-]  Viscosity[cP] 
PVTG
  39.95    1.0  0.029007223  0.0094358857
           0.5  0.029007223  0.0094358857
           0.0  0.029007223  0.0094358857
 / 
  40.0     1.010  0.0289717643  0.0094359307
           0.501  0.0289717643  0.0094359307
           0.000  0.0289717643  0.0094359307
 / 
  40.05    1.0  0.0289363942  0.0094359758
           0.5  0.0289363942  0.0094359758
           0.0  0.0289363942  0.0094359758
 / 
  40.1     1.0  0.0289011123  0.0094360209
           0.5  0.0289011123  0.0094360209
           0.0  0.0289011123  0.0094360209
 /
 /

INCLUDE
'${dic['exe']}/${dic['fol']}/preprocessing/TABLES.INC' /

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

RVVD
0   0.0
${dic['dims'][2]} 0.0 /

RV
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
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'tensor3d':
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
'INJ0'	${max(1, 1+mt.floor(dic['noCells'][1]/2))}	${max(1, 1+mt.floor(dic['noCells'][1]/2))}	1	${dic['noCells'][2]}	'OPEN'	1*	1*	${dic['diameter']} /
'PRO0'	${max(1, 1+mt.floor(dic['noCells'][1]/2))} ${max(1, 1+mt.floor(dic['noCells'][1]/2))}	1	${0*dic['noCells'][2]+1}	'OPEN' 1*	1*	${dic['diameter']} /
% else:
%if dic['grid'] == 'core':
'INJ0'	1	${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	'OPEN' 1*	${dic["jfactor"]}	 /
'PRO0'	1 ${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	'OPEN' 1*	${dic["jfactor"]} /
%else:
'INJ0'	${max(1, 1+mt.floor(dic['noCells'][1]/2))}	${max(1, 1+mt.floor(dic['noCells'][1]/2))}	1	${dic['noCells'][2]}	'OPEN'	1*	${dic["jfactor"]}	 /
'PRO0'	${max(1, 1+mt.floor(dic['noCells'][1]/2))} ${max(1, 1+mt.floor(dic['noCells'][1]/2))}	1	${0*dic['noCells'][2]+1}	'OPEN' 1*	${dic["jfactor"]} /
%endif
%endif
% if dic["pvMult"] == 0 or dic['grid']== 'core':
% if dic['grid']== 'core':
'PRO1'	${dic['noCells'][0]}	${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	${1+mt.floor(dic['noCells'][2]/2)}	'OPEN' 1*	${dic["jfactor"]} /
% elif dic['grid'] != 'cartesian' and dic['grid'] != 'tensor3d':
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
'RATE' ${f"{dic['inj'][j][4] / 0.6785064 : E}"}  1* 400/
%endif
/
WCONPROD
'PRO0' ${'OPEN' if dic['inj'][j][4] < 0 else 'SHUT'} 'GRAT' 2* ${f"{abs(dic['inj'][j][4]) / 0.0850397 : E}"} 2* ${.9*dic['pressure']}/
% if dic['grid'] == 'core':
'PRO1' 'OPEN' 'BHP' 5* ${dic['pressure']}/
%endif
% if dic["pvMult"] == 0:
% if dic['grid'] == 'cartesian' or dic['grid'] == 'tensor3d':
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