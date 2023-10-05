<%
import math as mt
%>"""Set the full path to the flow executable and flags"""
${flow} --enable-tuning=true --enable-opm-rst-file=true --linear-solver=cprw

"""Set the model parameters"""
h2store hwell #Model (co2store/h2store)
cartesian2d 10 #Grid type (radial/cake/cartesian2d/cartesian) and size (theta[in degrees]/theta[in degrees]/width[m]/anynumber(the y size is set equal to the x one))
10 50         #Reservoir dimensions [m] (Lenght and height)
10 100 0      #Number of x- and z-cells [-] and exponential factor for the telescopic x-gridding (0 to use an equidistance partition)
0.15 0 0     #Well diameter [m] and well transmiscibility (0 to use the computed one internally in Flow)
4e6 50 0     #Pressure [Pa] on the top and uniform temperature [°] (!!!!!!!Currently only for these pressure and temperature values, it is in the TODO list to extend this)
1e8 0       #Pore volume multiplier on the boundary [-] (0 to use well producers instead) and deactivate cross flow within the wellbore (see XFLOW in OPM Manual)
0 5 15       #Activate perforations [-], number of well perforations [-], and lenght [m]
1 Killough 0  #Number of layers [-], hysteresis (1 to activate), and econ for the producer (for h2 models)
0 0 0 0 0 0 0 #Ini salt conc [kg/m3], salt sol lim [kg/m3], prec salt den [kg/m3], gamma [-], phi_r [-], npoints [-], and threshold [-]  (all entries for saltprec)
0 #The function for the reservoir surface

"""Set the saturation functions"""
krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw             #Wetting rel perm saturation function [-]
krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn      #Non-wetting rel perm saturation function [-]
pec * ((sw - swi) / (1.0 - swi)) ** (-(1.0 / npe))        #Capillary pressure saturation function [Pa]

"""Properties saturation functions"""
"""swi [-], sni [-], krn [-], krw [-], pec [Pa], nkrw [-], nkrn [-], npe [-], threshold cP evaluation, ignore swi for cP"""
SWI5 0.2 SNI5  0.05 KRW5  1 KRN5  0.75 PRE5  .4e6 NKRW5 2 NKRN3 2 HNPE5 1.2 THRE5  1e-2 IGN1 0
SWI5 0.2 SNI5  0.30 KRW5  1 KRN5  0.75 PRE5  .4e6 NKRW5 2 NKRN3 4 HNPE5 1.2 THRE5  1e-2 IGN1 0

"""Properties rock"""
"""Kxy [mD], Kz [mD], phi [-], thickness [m]"""
PERMXY5 700.15 PERMZ5 70.015 PORO5 0.30 THIC2 50

"""Define the injection values""" 
"""injection time [d], time step size to write results [d], maximum time step [d], fluid (0 wetting, 1 non-wetting), injection rates [kg/day]"""
% for i in range(mt.floor(time/(tperiodi + tperiodp))):
${tperiodi} ${tperiodi} 1 1 ${qi}
${tperiodp} ${tperiodp} 1 1 ${-qp} 3.5e6
% endfor