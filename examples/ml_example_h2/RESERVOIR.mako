-- Copyright (C) 2023 NORCE

----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS 
25 1 20 /


EQLDIMS
/

TABDIMS
4 1* 10000 /

OIL
GAS
DISGAS
H2STORE

METRIC

START
1 'JAN' 2000 /


WELLDIMS
6 20 6 6 /

UNIFIN
UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INIT

INCLUDE
  'CAKE.INC' /

EQUALS
PERMX  10.0 1* 1* 1* 1* 1 5 /
PERMX  0.0001 1* 1* 1* 1* 6 10 /
PERMX  700.15 1* 1* 1* 1* 11 15 /
PERMX  0.01 1* 1* 1* 1* 16 20 /
/

EQUALS
PERMZ  10.0 1* 1* 1* 1* 1 5 /
PERMZ  0.0001 1* 1* 1* 1* 6 10 /
PERMZ  700.15 1* 1* 1* 1* 11 15 /
PERMZ  0.01 1* 1* 1* 1* 16 20 /
/

COPY 
PERMX PERMY /
/

EQUALS
PORO  0.1 1* 1* 1* 1* 1 5 /
PORO  0.1 1* 1* 1* 1* 6 10 /
PORO  0.25 1* 1* 1* 1* 11 15 /
PORO  0.1 1* 1* 1* 1* 16 20 /
/

----------------------------------------------------------------------------
EDIT
----------------------------------------------------------------------------
BOX
25 25 1 1 1* 1* / 
MULTPV
20*10.0 /
ENDBOX


----------------------------------------------------------------------------
PROPS
----------------------------------------------------------------------------

INCLUDE
'TABLES.INC' /


----------------------------------------------------------------------------
REGIONS
----------------------------------------------------------------------------

EQUALS
SATNUM  1 1* 1* 1* 1* 1 5 /
SATNUM  2 1* 1* 1* 1* 6 10 /
SATNUM  3 1* 1* 1* 1* 11 15 /
SATNUM  4 1* 1* 1* 1* 16 20 /
/


----------------------------------------------------------------------------
SOLUTION
---------------------------------------------------------------------------
EQUIL
 0 40.0 100 0 0 0 1 1 0 /
--PRESSURE
--% for i in range(dic['noCells'][2]):
--	25*40.0009984221676
--% endfor
--/
--SGAS
--	500*0.0 /
RTEMPVD
0   50.0
100.0 50.0 /
RSVD
0   0.0
100.0 0.0 /
RS
500*0.0 /


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
 'INJ0'  1  /
 'PRO0'  1  /
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
 'INJ0'  1  /
 'PRO0'  1  /
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


----------------------------------------------------------------------------
SCHEDULE
----------------------------------------------------------------------------
RPTRST
 'BASIC=2' FLOWS FLORES DEN VISC /

WELSPECS
'INJ0'	'G1'	1 1	1*	'GAS' 2* 'STOP' /
'PRO0'	'G1'	1 1	1*	'GAS' 2* 'STOP' /
/
COMPDAT
'INJ0'	1	1	1	20	'OPEN'	1*	1*	0.25 /
'PRO0'	1 1	1	20	'OPEN' 1*	1*	0.25 /
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' OPEN
'RATE'  2.351843E+06  1* 400/
/
WCONPROD
'PRO0' SHUT 'GRAT' 2*  2.351843E+06 2* 36.0/
/
WECON
'PRO0' 1*  2.234251E+06 /
/
TSTEP
${time}
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' SHUT
'RATE'  0.000000E+00  1* 400/
/
WCONPROD
'PRO0' SHUT 'GRAT' 2*  0.000000E+00 2* 36.0/
/
WECON
'PRO0' 1*  0.000000E+00 /
/
TSTEP
90*1.0
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' SHUT
'RATE' -4.703685E+06  1* 400/
/
WCONPROD
'PRO0' OPEN 'GRAT' 2*  4.703685E+06 2* 36.0/
/
WECON
'PRO0' 1*  4.468501E+06 /
/
TSTEP
7*1.0
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' OPEN
'RATE'  4.703685E+06  1* 400/
/
WCONPROD
'PRO0' SHUT 'GRAT' 2*  4.703685E+06 2* 36.0/
/
WECON
'PRO0' 1*  4.468501E+06 /
/
TSTEP
7*1.0
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' SHUT
'RATE' -4.703685E+06  1* 400/
/
WCONPROD
'PRO0' OPEN 'GRAT' 2*  4.703685E+06 2* 36.0/
/
WECON
'PRO0' 1*  4.468501E+06 /
/
TSTEP
7*1.0
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' OPEN
'RATE'  4.703685E+06  1* 400/
/
WCONPROD
'PRO0' SHUT 'GRAT' 2*  4.703685E+06 2* 36.0/
/
WECON
'PRO0' 1*  4.468501E+06 /
/
TSTEP
7*1.0
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' SHUT
'RATE' -4.703685E+06  1* 400/
/
WCONPROD
'PRO0' OPEN 'GRAT' 2*  4.703685E+06 2* 36.0/
/
WECON
'PRO0' 1*  4.468501E+06 /
/
TSTEP
7*1.0
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' OPEN
'RATE'  4.703685E+06  1* 400/
/
WCONPROD
'PRO0' SHUT 'GRAT' 2*  4.703685E+06 2* 36.0/
/
WECON
'PRO0' 1*  4.468501E+06 /
/
TSTEP
7*1.0
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' SHUT
'RATE' -4.703685E+06  1* 400/
/
WCONPROD
'PRO0' OPEN 'GRAT' 2*  4.703685E+06 2* 36.0/
/
WECON
'PRO0' 1*  4.468501E+06 /
/
TSTEP
7*1.0
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' OPEN
'RATE'  4.703685E+06  1* 400/
/
WCONPROD
'PRO0' SHUT 'GRAT' 2*  4.703685E+06 2* 36.0/
/
WECON
'PRO0' 1*  4.468501E+06 /
/
TSTEP
7*1.0
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' SHUT
'RATE' -4.703685E+06  1* 400/
/
WCONPROD
'PRO0' OPEN 'GRAT' 2*  4.703685E+06 2* 36.0/
/
WECON
'PRO0' 1*  4.468501E+06 /
/
TSTEP
7*1.0
/
TUNING
1e-2 1.0 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' OPEN
'RATE'  4.703685E+06  1* 400/
/
WCONPROD
'PRO0' SHUT 'GRAT' 2*  4.703685E+06 2* 36.0/
/
WECON
'PRO0' 1*  4.468501E+06 /
/
TSTEP
7*1.0
/
