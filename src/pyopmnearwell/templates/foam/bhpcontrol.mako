-- This reservoir simulation deck is made available under the Open Database
-- License: http://opendatacommons.org/licenses/odbl/1.0/. Any rights in
-- individual contents of the database are licensed under the Database Contents
-- License: http://opendatacommons.org/licenses/dbcl/1.0/

-- Copyright (C) 2015 Statoil
-- Copyright (C) 2019 SINTEF Digital
-- Copyright (C) 2020 NORCE 

-- This is the dataset used for the example in:
-- Sandve, T.H., Sævareid, O. & Aavatsmark, I. Dynamic PVT model for CO2-EOR black-oil 
-- simulations. Comput Geosci (2022). https://doi.org/10.1007/s10596-022-10133-x

-- The files have been converted to templates to allow for grid refinment and simulating
-- with different injection strategies. For the original deck, see:
-- https://github.com/OPM/opm-publications/tree/master/dynamic_blackoil

-- The foam keywrods and tables are taken from:
-- https://github.com/OPM/opm-tests/blob/master/spe1_foam/SPE1FOAM.DATA
-------------------------------------------------------------------------
RUNSPEC
-------------------------------------------------------------------------
DIMENS
${dic['nocells'][0]} ${dic['nocells'][0]} ${dic['nocells'][2]} /

EQLDIMS
/

TABDIMS
/

OIL
GAS
WATER
DISGAS
FOAM

FIELD

START
1 'JAN' 1987 /

WELLDIMS
3 ${dic['nocells'][2]} 2 2 /

UNIFOUT
-------------------------------------------------------------------------
GRID
-------------------------------------------------------------------------
% if dic['write'] == 1:
INIT
% else:
GRIDFILE 
0 0 /
% endif

% if dic['grid']== 'cpg3d':
INCLUDE
  ${dic['grid_file']} /
%else:
DX 	
${dic['nocells'][0]*dic['nocells'][0]*dic['nocells'][2]}*${dic['dims'][0]/dic['nocells'][0]} /

DY	
${dic['nocells'][0]*dic['nocells'][0]*dic['nocells'][2]}*${dic['dims'][0]/dic['nocells'][0]} /

DZ
%for i in range(dic['satnum']):
${dic['nocells'][0]*dic['nocells'][0]*dic['rock'][i][4]}*${dic['rock'][i][3]/(dic['rock'][i][4])}
%endfor
/

TOPS
${dic['nocells'][0]*dic['nocells'][0]}*8325 /
% endif

PORO
%for i in range(dic['satnum']):
${dic['nocells'][0]*dic['nocells'][0]*dic['rock'][i][4]}*${dic['rock'][i][2]}
%endfor
/

PERMX
%for i in range(dic['satnum']):
${dic['nocells'][0]*dic['nocells'][0]*dic['rock'][i][4]}*${dic['rock'][i][0]}
%endfor
/

PERMY
%for i in range(dic['satnum']):
${dic['nocells'][0]*dic['nocells'][0]*dic['rock'][i][4]}*${dic['rock'][i][0]}
%endfor
/

PERMZ
%for i in range(dic['satnum']):
${dic['nocells'][0]*dic['nocells'][0]*dic['rock'][i][4]}*${dic['rock'][i][1]}
%endfor
/
-------------------------------------------------------------------------
PROPS
-------------------------------------------------------------------------
PVTW
14.7 1.0 3.3E-6 0.70 0.0 / 

ROCK
14.7 5E-6 /

SOF2 
0	0.0	
0.0889	0.0	
0.1778 	0.0 		 
0.2667 	0.0	
0.30	0.0	
0.3556	0.0123	
0.4444	0.0835	
0.5333	0.2178	
0.6222	0.4153	
0.7111	0.6769	
0.80	1.0	/

SSFN 
0.0 0.0 0.0
1.0 1.0 1.0
/

DENSITY 
38.53 62.4 0.06864 /
  
SDENSITY
0.1169088418 /

PVDG
14.700	211.416	0.01070
 500.0	5.92420	0.01270
1000.0	2.85060	0.01340
1200.0	2.34410	0.01360
1500.0	1.84570	0.01450
1800.0	1.52020	0.01530
2000.0	1.36020	0.01590
2302.3	1.17510	0.01700
2500.0	1.10250	0.01770
3000.0	0.98030	0.01950
3500.0	0.91160	0.02140
4000.0	0.86210	0.02320
4500.0	0.82240	0.02500
4800.0	0.80320	0.02610			
/

PVDS
14.700	233.214	0.01100
 500.0	5.60220	0.01200
1000.0	2.53100	0.01300
1200.0	2.03540	0.01400
1500.0	1.55930	0.01600
1800.0	1.26570	0.01800
2000.0	1.12960	0.01900
2302.3	0.98030	0.02200
2500.0	0.90850	0.02300
3000.0	0.78070	0.02700
3500.0	0.69940	0.03100
4000.0	0.64300	0.03400
4500.0	0.60170	0.03700
4800.0	0.58170	0.03800	
/

PVTO
0.0000	  14.7	1.0348	0.310 /
0.1176	 500.0	1.1017	0.295 /
0.2226	1000.0	1.1478	0.274 /
0.2677	1200.0	1.1677	0.264 /
0.3414	1500.0	1.1997	0.249 /
0.4215	1800.0	1.2350	0.234 /
0.4790	2000.0	1.2600	0.224 /
0.5728	2302.3	1.3010	0.208 /
0.6341	2500.0	1.3278	0.200 /
0.7893	3000.0	1.3956	0.187 /
0.9444	3500.0	1.4634	0.175 /
1.0995	4000.0	1.5312	0.167 /
1.2547	4500.0	1.5991	0.159 /
1.3478	4800.0	1.6398	0.155 
5500.0	1.6305	0.165 /	 
/

SWFN
0.2000	0   	45.00
0.2899  0.0022 	19.03
0.3778	0.0180	10.07
0.4667	0.0607	 4.90
0.5556	0.1438	 1.8
0.6444	0.2809	 0.50
0.7000	0.4089	 0.05
0.7333	0.4855	 0.01		
0.8222	0.7709	 0.0
0.9111	1.00	 0.0
1.0000	1.00	 0.0 /
 
SGFN
0	0.0	0
0.05	0.0 	0
0.0889	0.001	0
0.1778	0.010	0
0.2667	0.030	0.001
0.3556	0.050	0.001
0.4443	0.100	0.030
0.5333	0.200	0.80
0.6222	0.350	3.0
0.650	0.390	4.0
0.7111	0.560	8.0
0.80	1.0	    30.0/

SOF3
0	    0.0	    0.0
0.0889	0.0	    0.0
0.150  	1*	    0.0
0.1778 	0.0     0.011	 
0.2667 	0.0	    0.037
0.30	0.0	    1*
0.3556	0.0123	0.0878
0.4444	0.0835	0.1715
0.5333	0.2178	0.2963
0.6222	0.4153	0.4705
0.7111	0.6769	0.7023
0.75	1*	    0.88
0.80	1.0	    1.0 /

FOAMROCK
1 2000 /

FOAMMOB
0.00   1.0
0.01   0.5
0.02   0.2
0.03   0.1
0.04   0.1 /

FOAMADS
0.00   0.00000
0.01   0.00001
0.02   0.00002
0.03   0.00003
0.04   0.00003 /
-------------------------------------------------------------------------
SOLUTION
-------------------------------------------------------------------------
% if dic['write'] == 1:
RPTRST
'BASIC=2' DENG DENO DENW BO BG BW KRG KRO KRW PCOW PCOG VGAS VOIL VWAT FOAM
/
% endif

EQUIL
8400 ${dic["pressure"]} 8450 0 8300 0 1 0 0 /

RSVD
8300 0.5728
8450 0.5728 /
-------------------------------------------------------------------------
SUMMARY
-------------------------------------------------------------------------
PERFORMA
FPR 

FGIP

FWIP

FOIP

FGIR

FWIR

FVIT

FGIT

FWIT

FGPR

FWPR

FOPR

FGPT

FWPT

FOPT

FNIT

FNPT

FNIP
 
WBHP
  'INJW'
  'INJG'
  'PROD'/
WGIR
  'INJW'
  'INJG'
  'PROD'/
WGIT
  'INJW'
  'INJG'
  'PROD'/
WGPR
  'INJW'
  'INJG'
  'PROD'/
WGPT
  'INJW'
  'INJG'
  'PROD'/
WOIR
  'INJW'
  'INJG'
  'PROD'/
WOIT
  'INJW'
  'INJG'
  'PROD'/
WOPR
  'INJW'
  'INJG'
  'PROD'/
WOPT
  'INJW'
  'INJG'
  'PROD'/
WWIR
  'INJW'
  'INJG'
  'PROD'/
WWIT
  'INJW'
  'INJG'
  'PROD'/
WWPR
  'INJW'
  'INJG'
  'PROD'/
WWPT
  'INJW'
  'INJG'
  'PROD'/
FTIRFOA
FTITFOA
FTPRFOA
FTPTFOA
FTADSFOA
FTDCYFOA
FTMOBFOA
FTIPTFOA
-------------------------------------------------------------------------
SCHEDULE
-------------------------------------------------------------------------
% if dic['write'] == 1:
RPTRST
'BASIC=2' DENG DENO DENW BO BG BW KRG KRO KRW PCOW PCOG VGAS VOIL VWAT FOAM
/
% endif
WELSPECS
	'PROD'	'G1'	${dic['nocells'][0]}	${dic['nocells'][0]}	1*	'OIL' /
	'INJW'	'INJ'	1	1	1*	'WATER' /
	'INJG'	'INJ'	1	1	1*	'GAS' /
/
COMPDAT
	'PROD'	${dic['nocells'][0]}	${dic['nocells'][0]}	${dic['nocells'][2]-dic['rock'][-1][4]+1}	${dic['nocells'][2]} 'OPEN' 2* ${dic["diameter"]}  /
	'INJW'	1	1	1	${dic['rock'][0][4]}	'OPEN'	2*	${dic["diameter"]}  /
	'INJG'	1	1	1	${dic['rock'][0][4]}	'OPEN'	2*	${dic["diameter"]}  /
/
WCONPROD
'PROD' 'OPEN' 'BHP' 5* ${dic["probhp"]} /
/

% for j in range(len(dic['inj'])):
TUNING
1e-2 ${dic['inj'][j][2]} 1e-10 2* 1e-12/
/
/
WCONINJE
'INJW' 'WATER' ${'OPEN' if dic['inj'][j][3] == 0 else 'SHUT'}
'RATE' ${f"{dic['inj'][j][4]}"}  1* ${dic["injbhp"]}/
'INJG' 'GAS' ${'SHUT' if dic['inj'][j][3] == 0 else 'OPEN'}
'RATE' ${f"{dic['inj'][j][4]}"}  1* ${dic["injbhp"]}/
/

WFOAM
'INJG'  ${dic['inj'][j][3]}/
/

TSTEP
${round(dic['inj'][j][0]/dic['inj'][j][1])}*${dic['inj'][j][1]}
/
% endfor