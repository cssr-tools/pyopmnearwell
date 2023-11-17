"""Set the full path to the flow executable and flags"""
${FLOW} --enable-opm-rst-file=true

"""Set the model parameters"""
co2store base   #Model (co2store/h2store)
cake 60         #Grid type (radial/cake/cartesian2d/cartesian/cave) and size (theta[in degrees]/theta[in degrees]/width[m]/anynumber(the y size is set equal to the x one))
400 1          #Reservoir dimensions [m] (Length and height)
20 1 0          #Number of x- and z-cells [-] and exponential factor for the telescopic x-gridding (0 to use an equidistance partition)
0.1 0 0           #Well diameter [m], well transmiscibility (0 to use the computed one internally in Flow), and remove the smaller cells than the well diameter
${PRESSURE} ${TEMPERATURE}  0 #Pressure [Pa] on the top, uniform temperature [°], and initial phase in the reservoir (0 wetting, 1 non-wetting)
1e5 0           #Pore volume multiplier on the boundary [-] (0 to use well producers instead) and deactivate cross flow within the wellbore (see XFLOW in OPM Manual)
0 5 10          #Activate perforations [-], number of well perforations [-], and length [m]
1 0 0           #Number of layers [-] and hysteresis (1 to activate) and econ for the producer (for h2 models)
0 0 0 0 0 0 0   #Ini salt conc [kg/m3], salt sol lim [kg/m3], prec salt den [kg/m3], gamma [-], phi_r [-], npoints [-], and threshold [-]  (all entries for saltprec)
0               #The function for the reservoir surface

"""Set the saturation functions"""
krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw             #Wetting rel perm saturation function [-]
krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn      #Non-wetting rel perm saturation function [-]
pec * ((sw - swi) / (1.0 - sni - swi)) ** (-(1.0 / npe))  #Capillary pressure saturation function [Pa]

"""Properties saturation functions"""
"""swi [-], sni [-], krn [-], krw [-], pec [Pa], nkrw [-], nkrn [-], npe [-], threshold cP evaluation, ignore swi for cP"""
SWI2  0.14 SNI2  0.1 KRW2  1 KRN2  1 PRE2  8655 NNKRW2 2 NNKRN2 2 HNPE2 2 THRE2  1e-4 IGN1  0

"""Properties rock"""
"""Kxy [mD], Kz [mD], phi [-], thickness [m]"""
PERMXY5 ${PERMX} PERMZ5 ${PERMZ} PORO5 0.25 THIC5 1

"""Define the injection values""" 
"""injection time [d], time step size to write results [d], maximum time step [d], injected fluid (0 wetting, 1 non-wetting), injection rates [kg/day]"""
10 1e-1 1e-1 1 ${INJECTION_RATE}