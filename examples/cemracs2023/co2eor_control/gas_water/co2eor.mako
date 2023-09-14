"""Set the full path to the flow executable and flags"""
${flow} --enable-tuning=true --enable-opm-rst-file=true --linear-solver=cprw --relaxed-max-pv-fraction=0

"""Set the model parameters"""
co2eor bhpcontrol       #Model (co2store/h2store)
cartesian2d 1 #Grid type (radial/cake/cartesian2d/cartesian) and size (theta[in degrees]/theta[in degrees]/width[m]/anynumber(the y size is set equal to the x one))
3500 100     #Reservoir dimensions [ft] (Lenght and height)
7 9 0        #Number of x- and z-cells [-] and exponential factor for the telescopic x-gridding (0 to use an equidistance partition)
0 0 0        #Well diameter [m], well transmiscibility (0 to use the computed one internally in Flow), and remove the smaller cells than the well diameter
0 0  0       #Pressure [Pa] on the top, uniform temperature [°], and initial phase in the reservoir (0 wetting, 1 non-wetting)
0 0          #Pore volume multiplier on the boundary [-] (0 to use well producers instead) and deactivate cross flow within the wellbore (see XFLOW in OPM Manual)
0 0 0        #Activate perforations [-], number of well perforations [-], and lenght [m]
3 0 0        #Number of layers [-], hysteresis (1 to activate), and econ for the producer (for h2 models)
0 0 0 0 0 0 0 #Ini salt conc [kg/m3], salt sol lim [kg/m3], prec salt den [kg/m3], gamma [-], phi_r [-], npoints [-], and threshold [-]  (all entries for saltprec)
0            #The function for the reservoir surface

"""Set the saturation functions"""
krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw             #Wetting rel perm saturation function [-]
krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn      #Non-wetting rel perm saturation function [-]
pec * ((sw - swi) / (1.0 - sni - swi)) ** (-(1.0 / npe))  #Capillary pressure saturation function [Pa]

"""Properties saturation functions"""
"""swi [-], sni [-], krn [-], krw [-], pec [Pa], nkrw [-], nkrn [-], npe [-], threshold cP evaluation, ignore swi for cP"""
SWI1 0. SNI1 0. KRW1 1 KRN1 1 PEC1 0 NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4 IGN1 0
SWI1 0. SNI1 0. KRW1 1 KRN1 1 PEC1 0 NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4 IGN1 0
SWI1 0. SNI1 0. KRW1 1 KRN1 1 PEC1 0 NKRW1 2 NKRN1 2 NPE1 2 THRE1 1e-4 IGN1 0

"""Properties rock"""
"""Kxy [mD], Kz [mD], phi [-], thickness [ft], number of cells in the z dir [-]"""
PERMXY1 500 PERMZ1 50 PORO1 0.3 THIC1 20 NZ1 3
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