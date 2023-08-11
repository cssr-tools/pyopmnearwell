-- Copyright (C) 2023 NORCE

----------------------------------------------------------------------------
RUNSPEC
----------------------------------------------------------------------------
DIMENS
400 1 1 /

EQLDIMS
/

TABDIMS
1 1* 10000 /

WATER
GAS
CO2STORE
DIFFUSE
DISGASW

METRIC

START
1 'JAN' 2000 /


WELLDIMS
6 1 6 6 /

UNIFIN
UNIFOUT
----------------------------------------------------------------------------
GRID
----------------------------------------------------------------------------
INIT

INCLUDE
  'CAKE.INC' /

EQUALS
PERMX  ${permeability_x} 1* 1* 1* 1* 1 1 /
/

EQUALS
PERMZ  ${permeability_x} 1* 1* 1* 1* 1 1 /
/

COPY 
PERMX PERMY /
/

EQUALS
PORO  0.25 1* 1* 1* 1* 1 1 /
/

----------------------------------------------------------------------------
EDIT
----------------------------------------------------------------------------
BOX
400 400 1 1 1* 1* / 
MULTPV
1*40000000000.0 /
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
SATNUM  1 1* 1* 1* 1* 1 1 /
/

----------------------------------------------------------------------------
SOLUTION
---------------------------------------------------------------------------
EQUIL
 0 ${init_pressure} 0 0 0 0 1 1 0 /

RTEMPVD
0   ${temperature}
1.0 ${temperature} /

RVW
	400*.0 /

RPTRST 
 'BASIC=2' DEN VISC/

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
 'INJ0'  1  /
/

CGIT
 INJ0 /
/

CGITL
 INJ0 /
/

WGITL
 'INJ0'  1  /
/

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
'INJ0'	'G1'	1 1	1*	'GAS' /
/
COMPDAT
'INJ0'	1	1	1	1	'OPEN'	1*	1.0	 /
/
TUNING
1e-2 0.1 1e-10 2* 1e-12/
/
/
WCONINJE
'INJ0' 'GAS' OPEN
'RATE'  ${injection_rate}  1* 400/
/
TSTEP
100*0.1
/