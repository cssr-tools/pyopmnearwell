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
${(dic["hysteresis"]+1)*(dic['satnum']+dic['perforations'][0])} 1* 10000 /

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

WELLDIMS
${dic['noCells'][2]} ${dic['noCells'][2]} 1 ${dic['noCells'][2]} /

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
% elif dic['grid']== 'cave':
INCLUDE
  '${dic['exe']}/${dic['fol']}/preprocessing/CAVE.INC' /
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
% for i in range(dic['noCells'][2]):
PERMX  ${dic['rock'][int(dic["layers"][i])][0]} 1* 1* 1* 1* ${i+1} ${i+1} /
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
% for i in range(dic['noCells'][2]):
PERMZ  ${dic['rock'][int(dic["layers"][i])][1]} 1* 1* 1* 1* ${i+1} ${i+1} /
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
% for i in range(dic['noCells'][2]):
PORO  ${dic['rock'][int(dic["layers"][i])][2]} 1* 1* 1* 1* ${i+1} ${i+1} /
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
% if dic['grid'] != 'cartesian' and dic['grid'] != 'cave':
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

INCLUDE
'${dic['exe']}/${dic['fol']}/preprocessing/TABLES.INC' /

SALTSOL
	${dic['salt_props'][1]} ${dic['salt_props'][2]}/
/

PERMFACT
0.0 1.427e-05
0.8 1.427e-05
0.81 0.002776688986880076
0.82 0.011094049904030737
0.83 0.024915453264443454
0.84 0.04418300653594782
0.85 0.06882022471910128
0.86 0.09873462214411233
0.87 0.13382018987643707
0.88 0.17395973154362412
0.89 0.21902703809913965
0.9 0.2688888888888889
0.91 0.3234068723155018
0.92 0.382439024390244
0.93 0.44584128755010144
0.94 0.5134687953555873
0.95 0.5851769911504421
0.96 0.6608225905463472
0.97 0.7402643987874704
0.98 0.8233639947437581
0.99 0.9099862935668768
1.0 1.0 /
/

----------------------------------------------------------------------------
REGIONS
----------------------------------------------------------------------------

EQUALS
% for i in range(dic['satnum']):
SATNUM  ${i+1} 1* 1* 1* 1* ${1+i*round(dic['noCells'][2]/dic['satnum'])} ${(i+1)*round(dic['noCells'][2]/dic['satnum'])} /
% endfor
% if dic['perforations'][0] == 1:
% for i in range(dic['perforations'][1]):
SATNUM  ${dic['satnum']+1} 1 ${dic['perforations'][2]} 1* 1* ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} ${(i+1)*round(dic['noCells'][2]/(dic['perforations'][1]+1))} /
% endfor
% endif
/

----------------------------------------------------------------------------
SOLUTION
---------------------------------------------------------------------------

PRESSURE
% for i in range(dic['noCells'][2]):
	${dic['noCells'][0]*dic['noCells'][1]}*${dic['pressure']+1e-5*i*998.108*9.81*dic['dims'][2]/dic['noCells'][2]}
% endfor
/
SWAT
	${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*1.0 /
SALT
	${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*${dic['salt_props'][0]} /
SALTP
	${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*.0 /
RVW
	${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*.0 /
RS
	${dic['noCells'][0]*dic['noCells'][1]*dic['noCells'][2]}*.0 /
RTEMPVD
0   ${dic['temperature']}
${dic['dims'][2]} ${dic['temperature']} /

RPTRST 
 'BASIC=2' DEN VISC /

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
 'BASIC=2' DEN VISC /

WELSPECS
% for i in range(0*dic['noCells'][2]+1):
'INJ${i}'	'G1'	1	1	1*	'GAS' /
% endfor
/

COMPDAT
% for i in range(0*dic['noCells'][2]+1):
% if dic["jfactor"] == 0:
'INJ${i}'	1	1	${i+1}	${i+1}	'OPEN'	1*	1*	${dic['diameter']} 3* X /
% else:
'INJ${i}'	1	1	${0*i+1}	${dic['noCells'][2]}	'OPEN'	1*	${dic["jfactor"]}	4* X /
%endif
% endfor
/

% for j in range(len(dic['inj'])):
TUNING
1e-2 ${dic['inj'][j][2]} 1e-10 2* 1e-12/
/
/
WCONINJE
% for i in range(dic['noCells'][2]*0+1):
% if dic['inj'][j][3] > 0:
'INJ${i}' 'GAS' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4] / (dic['noCells'][2]*1.86843) : E}"}  1* 400/
% else:
'INJ${i}' 'WATER' ${'OPEN' if dic['inj'][j][4] > 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4] / (dic['noCells'][2]*998.108) : E}"}  1* 400/
%endif
%endfor
/
TSTEP
${round(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor