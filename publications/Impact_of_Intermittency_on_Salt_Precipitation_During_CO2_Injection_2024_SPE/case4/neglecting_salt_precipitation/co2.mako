"""Set the full path to the flow executable and flags"""
flow --linear-solver=cprw --enable-tuning=true --enable-opm-rst-file=true --enable-well-operability-check=false --min-time-step-before-shutting-problematic-wells-in-days=1e-99 --linear-solver-ignore-convergence-failure=false

"""Set the model parameters"""
co2store salinity     #Model (co2store/h2store/co2eor/saltprec)
cake 60    #Grid type (radial/cartesian/cake) and size (width/theta/theta [in degrees])
10000 100       #Reservoir dimensions [m] (Lenght and height)
150 100 7.1  #Number of x- and z-cells [-] and exponential factor for the telescopic x-gridding
0.1 0 0      #Well diameter [m], well transmiscibility (0 to use the computed one internally in Flow), and remove the smaller cells than the well diameter
21.3e6 40 0  #Pressure [Pa] on the top, uniform temperature [°], and initial phase in the reservoir (0 wetting, 1 non-wetting)
-1 0    #Pore volume multiplier on the boundary [-] (0 to use well producers instead) and deactivate cross flow within the wellbore (see XFLOW in OPM Manual)
0 2 10       #Activate perforation [-], number of well perforations [-], and number of x-direction cells [-]
4 Killough 0 8.5e-10       #Number of layers [-], hysteresis (1 to activate), and econ for the producer (for h2 models)
2.72      #Salinity
0            #The function for the reservoir surface

"""Set the saturation functions"""
((sw - swi) / (1.0 - swi - sni)) ** 4.0    #Wetting rel perm saturation function [-]
(1-((sw - swi) / (1.0 - swi - sni)) ** 2.0) * (1-(sw - swi) / (1.0 - swi - sni)) ** 2    #Non-wetting rel perm saturation function [-]
pec * (((sw - swi) / (1. - swi)) ** (-(1./npe)) - 1.) ** (1. - npe) #Capillary pressure saturation function [Pa]

"""Properties sat functions"""
"""swi [-], swrg [-], krg [-], krw [-], pe [Pa], threshold cP evaluation, ignore swi for cP? (sl* for cplog)"""
SWI2 0.14 SNI2 0.1 KRW2 1 KRN2 1 PEC2 8654.99 NKRW2 0.457 NKRN2 0.457 NPE2 0.457 THRE2 6e-4 IGN1 0.28
SWI3 0.12 SNI3 0.1 KRW3 1 KRN3 1 PEC3 6120.00 NKRW3 0.457 NKRN3 0.457 NPE3 0.457 THRE3 6e-4 IGN3 0.23
SWI4 0.12 SNI4 0.1 KRW4 1 KRN4 1 PEC4 3870.63 NKRW4 0.457 NKRN4 0.457 NPE4 0.457 THRE4 6e-4 IGN4 0.215
SWI5 0.12 SNI5 0.1 KRW5 1 KRN5 1 PEC5 3060.00 NKRW5 0.457 NKRN5 0.457 NPE5 0.457 THRE5 6e-4 IGN5 0.205
SWI2 0.14 SNI2 0.15 KRW2 1 KRN2 1 PEC2 8654.99 NKRW2 0.457 NKRN2 0.457 NPE2 0.457 THRE2 6e-4 IGN1 0.28
SWI3 0.12 SNI3 0.15 KRW3 1 KRN3 1 PEC3 6120.00 NKRW3 0.457 NKRN3 0.457 NPE3 0.457 THRE3 6e-4 IGN3 0.23
SWI4 0.12 SNI4 0.15 KRW4 1 KRN4 1 PEC4 3870.63 NKRW4 0.457 NKRN4 0.457 NPE4 0.457 THRE4 6e-4 IGN4 0.215
SWI5 0.12 SNI5 0.15 KRW5 1 KRN5 1 PEC5 3060.00 NKRW5 0.457 NKRN5 0.457 NPE5 0.457 THRE5 6e-4 IGN5 0.205

"""Properties rock"""
"""Kx [mD], Kz [mD], phi [-], thickness [m]"""
PERMX2 101.324 PERMZ2 10.1324 PORO2 0.20 THIC1 25
PERMX3 202.650 PERMZ3 20.2650 PORO3 0.20 THIC1 25
PERMX4 506.625 PERMZ3 50.6625 PORO3 0.20 THIC1 25
PERMX5 1013.25 PERMZ5 101.325 PORO2 0.25 THIC1 25

"""Define the injection values""" 
"""injection time [d], time step size to write results [d], maximum time step [d], injected fluid (0 water, 1 co2), injection rates [kg/day]"""
5 5 .005 1 144000.0
360 360 .5 1 144000.0
% for _,control in enumerate(schedule[1:]):
${tperiod} ${tperiod} ${.5 if control==1 else 5} 1 ${control*144000.0}
% endfor