"""Set the full path to the flow executable and flags"""
${flow} --enable-opm-rst-file=true --linear-solver=cprw --relaxed-max-pv-fraction=0

"""Set the model parameters"""
co2eor bhpcontrol #Model (co2store/h2store)
cartesian   3500  #Grid type (radial/cake/cartesian2d/cartesian) and size (theta[in degrees]/theta[in degrees]/width[m]/anynumber(the y size is set equal to the x one))
3500 100          #Reservoir dimensions [ft] (length and height)
7 9 0             #Number of x- and z-cells [-] and exponential factor for the telescopic x-gridding (0 to use an equidistance partition)
0.5 0 0           #Well diameter [ft], well transmiscibility (0 to use the computed one internally in Flow), and remove the smaller cells than the well diameter
4000 10000 1000   #Pressure [Psia] on the top, injector max BHP [Psia], and producer min BHP [Psia]
0 0               #Pore volume multiplier on the boundary [-] (-1 to ignore; 0 to use well producers instead) and deactivate cross flow within the wellbore (see XFLOW in OPM Manual)
0 0 0             #Activate perforations [-], number of well perforations [-], and length [m]
3 0 0             #Number of layers [-], hysteresis (Killough, Carlson, or 0 to neglect it), and econ for the producer (for h2 models)
0 0 0 0 0 0 0     #Ini salt conc [kg/m3], salt sol lim [kg/m3], prec salt den [kg/m3], gamma [-], phi_r [-], npoints [-], and threshold [-]  (all entries for saltprec)
0                 #The function for the reservoir surface

"""Set the saturation functions"""
Using the original ones from the SPE5 deck         #Wetting rel perm saturation function [-]
Using the original ones from the SPE5 deck         #Non-wetting rel perm saturation function [-]
Using the original ones from the SPE5 deck         #Capillary pressure saturation function [Pa]

"""Properties saturation functions"""
"""swi [-], sni [-], krn [-], krw [-], pec [Pa], nkrw [-], nkrn [-], npe [-], threshold cP evaluation, ignore swi for cP"""
SWI1 0. SNI1 0. KRW1 0 KRN1 0 PEC1 0 NKRW1 0 NKRN1 0 NPE1 0 THRE1 0 IGN1 0 # Using the original ones from the SPE5 deck
SWI1 0. SNI1 0. KRW1 0 KRN1 0 PEC1 0 NKRW1 0 NKRN1 0 NPE1 0 THRE1 0 IGN1 0 # Using the original ones from the SPE5 deck
SWI1 0. SNI1 0. KRW1 0 KRN1 0 PEC1 0 NKRW1 0 NKRN1 0 NPE1 0 THRE1 0 IGN1 0 # Using the original ones from the SPE5 deck

"""Properties rock"""
"""Kxy [mD], Kz [mD], phi [-], thickness [ft], number of cells in the z dir [-]"""
PERMXY1 250 PERMZ1 25 PORO1 0.3 THIC1 20 NZ1 3
PERMXY2  50 PERMZ2 50 PORO2 0.3 THIC2 30 NZ2 3
PERMXY3 200 PERMZ3 25 PORO3 0.3 THIC3 50 NZ3 3

"""Define the injection values""" 
"""injection time [d], time step size to write results [d], maximum time step [d], fluid (0 wetting, 1 non-wetting), injection rates [kg/day]"""
% for _,control in enumerate(schedule):
% if control == 0:
${tperiod} ${tperiod} 1 0 ${qratew}
% else:
${tperiod} ${tperiod} 1 1 ${qrateg}
% endif
% endfor