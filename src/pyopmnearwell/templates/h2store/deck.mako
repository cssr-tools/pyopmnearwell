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
${(dic["hysteresis"]+1)*(dic['satnum']+dic['perforations'][0])} 1* 100000 /

OIL
GAS
VAPOIL
DIFFUSE

METRIC

START
1 'JAN' 2000 /

% if dic["hysteresis"] ==1:
SATOPTS
 HYSTER  /
% endif

WELLDIMS
5 ${dic['noCells'][2]} 5 5 /

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
% for i in range(dic['satnum']):
PERMX  ${dic['rock'][i][0]} 1* 1* 1* 1* ${1+i*round(dic['noCells'][2]/dic['satnum'])} ${(i+1)*round(dic['noCells'][2]/dic['satnum'])} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] != 'cartesian':
PERMX  ${dic['rock'][dic['satnum']][0]} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 1* 1* ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%else:
PERMX  ${dic['rock'][dic['satnum']][0]} ${round(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/

EQUALS
% for i in range(dic['satnum']):
PERMZ  ${dic['rock'][i][1]} 1* 1* 1* 1* ${1+i*round(dic['noCells'][2]/dic['satnum'])} ${(i+1)*round(dic['noCells'][2]/dic['satnum'])} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] != 'cartesian':
PERMZ  ${dic['rock'][dic['satnum']][1]} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 1* 1* ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%else:
PERMZ  ${dic['rock'][dic['satnum']][1]} ${round(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/

COPY 
PERMX PERMY /
/

EQUALS
% for i in range(dic['satnum']):
PORO  ${dic['rock'][i][2]} 1* 1* 1* 1* ${1+i*round(dic['noCells'][2]/dic['satnum'])} ${(i+1)*round(dic['noCells'][2]/dic['satnum'])} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] != 'cartesian':
PORO  ${dic['rock'][dic['satnum']][2]} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 1* 1* ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%else:
PORO  ${dic['rock'][dic['satnum']][2]} ${round(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/

% if dic["pvMult"] != 0:
----------------------------------------------------------------------------
EDIT
----------------------------------------------------------------------------
% if dic['grid'] != 'cartesian':
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

EQUALS
% for i in range(dic['satnum']):
SATNUM  ${i+1} 1* 1* 1* 1* ${1+i*round(dic['noCells'][2]/dic['satnum'])} ${(i+1)*round(dic['noCells'][2]/dic['satnum'])} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] != 'cartesian':
SATNUM  ${dic['satnum']+1} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 1* 1* ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} /
% else:
SATNUM  ${dic['satnum']+1} ${round(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} /
% endif
% endfor
% endif
/

% if dic["hysteresis"] ==1:
EQUALS
% for i in range(dic['satnum']):
IMBNUM  ${dic['satnum']+dic['perforations'][0]+1+i} 1* 1* 1* 1* ${1+i*round(dic['noCells'][2]/dic['satnum'])} ${(i+1)*round(dic['noCells'][2]/dic['satnum'])} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
% if dic['grid'] != 'cartesian':
IMBNUM  ${2*dic['satnum']+2} 1 ${sum(dic['x_centers']<dic['perforations'][2])} 1* 1* ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%else:
IMBNUM  ${2*dic['satnum']+2} ${round(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2)-sum(dic['x_centers']<dic['perforations'][2])} ${round(dic["noCells"][1] / 2) + sum(dic['x_centers']<dic['perforations'][2])} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} /
%endif
% endfor
% endif
/
% endif

----------------------------------------------------------------------------
SOLUTION
---------------------------------------------------------------------------
PRESSURE
% for i in range(dic['noCells'][2]):
	${dic['noCells'][0]*dic['noCells'][1]}*${dic['pressure']+1e-5*i*0.6785064*9.81*dic['dims'][2]/dic['noCells'][2]}
% endfor
/
SGAS
	${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*0.0 /
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
/

CGIRL
 INJ0 /
/

WGIRL
% for j in range(dic['noCells'][2]):
 'INJ0'  ${j+1}  /
% endfor
/

CGIT
 INJ0 /
/

CGITL
 INJ0 /
/

WGITL
% for j in range(dic['noCells'][2]):
 'INJ0'  ${j+1}  /
% endfor
/

FPR 

FGIP

FOIP

FGIR

FOIR

FGIT

FOIT

WGIR
/

WGIT
/

WBHP
/

RPR
/

ROIP
/

RGIP
/

----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
RPTRST
 'BASIC=2' FLOWS FLORES DEN VISC /

WELSPECS
'INJ0'	'G1'	${max(1, round(dic['noCells'][1]/2))} ${max(1, round(dic['noCells'][1]/2))}	1*	'GAS' /
% if dic["pvMult"] == 0:
% if dic['grid'] != 'cartesian':
'PRO0'	'G1'	${dic['noCells'][0]}	1	1*	'OIL' /
%else:
'PRO0'	'G1'	1	1	1*	'OIL' /
'PRO1'	'G1'	${dic['noCells'][0]}	1	1*	'OIL' /
'PRO2'	'G1'	1	${dic['noCells'][0]}	1*	'OIL' /
'PRO3'	'G1'	${dic['noCells'][0]}	${dic['noCells'][0]}	1*	'OIL' /
% endif
% endif
/
COMPDAT
% if dic["jfactor"] == 0:
'INJ0'	${max(1, round(dic['noCells'][1]/2))}	${max(1, round(dic['noCells'][1]/2))}	1	${dic['noCells'][2]}	'OPEN'	1*	1*	${dic['diameter']} /
% else:
'INJ0'	${max(1, round(dic['noCells'][1]/2))}	${max(1, round(dic['noCells'][1]/2))}	1	${dic['noCells'][2]}	'OPEN'	1*	${dic["jfactor"]}	 /
%endif
% if dic["pvMult"] == 0:
% if dic['grid'] != 'cartesian':
'PRO0 '	${dic['noCells'][0]}	1	1	${0*dic['noCells'][2]+1}	'OPEN' 1*	1*	${dic['diameter']} /
%else:
'PRO0'	1	1	1	${dic['noCells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
'PRO1'	${dic['noCells'][0]}	1	 1 ${dic['noCells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
'PRO2'	1	${dic['noCells'][0]} 1 ${dic['noCells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
'PRO3'	${dic['noCells'][0]}	${dic['noCells'][0]}	1	${dic['noCells'][2]}	'OPEN' 1*	1*	${dic['diameter']} /
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
% if dic["pvMult"] == 0:
WCONPROD
% if dic['grid'] != 'cartesian':
'PRO0' 'OPEN' 'BHP' 5* ${dic['pressure']}/
%else:
'PRO0' 'OPEN' 'BHP' 5* ${dic['pressure']}/
'PRO1' 'OPEN' 'BHP' 5* ${dic['pressure']}/
'PRO2' 'OPEN' 'BHP' 5* ${dic['pressure']}/
'PRO3' 'OPEN' 'BHP' 5* ${dic['pressure']}/
%endif
/
%endif
TSTEP
${round(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor