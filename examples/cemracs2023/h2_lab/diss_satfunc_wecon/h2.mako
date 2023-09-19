"""Set the full path to the flow executable and flags"""
${flow} --enable-tuning=true --enable-opm-rst-file=true --linear-solver=cprw --relaxed-max-pv-fraction=0

"""Set the model parameters"""
h2store base     #Model (co2store/h2store)
cake 60      #Grid type (radial/cake/cartesian2d/cartesian) and size (theta[in degrees]/theta[in degrees]/width[m]/anynumber(the y size is set equal to the x one))
2500 20      #Reservoir dimensions [m] (Lenght and height)
250 10 0     #Number of x- and z-cells [-] and exponential factor for the telescopic x-gridding (0 to use an equidistance partition)
0.25 0 0     #Well diameter [m] and well transmiscibility (0 to use the computed one internally in Flow)
4e6 50 0     #Pressure [Pa] on the top and uniform temperature [°] (!!!!!!!Currently only for these pressure and temperature values, it is in the TODO list to extend this)
1e4 0        #Pore volume multiplier on the boundary [-] (0 to use well producers instead) and deactivate cross flow within the wellbore (see XFLOW in OPM Manual)
0 5 15       #Activate perforations [-], number of well perforations [-], and lenght [m]
1 0 0.95  #Number of layers [-], hysteresis (1 to activate), and econ for the producer (for h2 models)
0 0 0 0 0 0 0 #Ini salt conc [kg/m3], salt sol lim [kg/m3], prec salt den [kg/m3], gamma [-], phi_r [-], npoints [-], and threshold [-]  (all entries for saltprec)
0*300-0*300*mt.exp(-(x**2)/(2*500**2)) - 0*100*mt.exp(-((x-500)**2)/(2*100**2)) #The function for the reservoir surface

"""Set the saturation functions"""
krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw             #Wetting rel perm saturation function [-]
krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn      #Non-wetting rel perm saturation function [-]
pec * ((sw - swi) / (1.0 - sni - swi)) ** (-(1.0 / npe)) #Capillary pressure saturation function [Pa]

"""Properties saturation functions"""
"""swi [-], sni [-], krn [-], krw [-], pec [Pa], nkrw [-], nkrn [-], npe [-], threshold cP evaluation, ignore swi for cP"""
SWI5  0.1 SNI5  0.1 KRW5  .8 KRN5  .2 PRE5  .4e6 NKRW5 4 NKRN3 3.5 HNPE5 1.2 THRE5  1e-4 IGN1 0

"""Properties rock"""
"""Kxy [mD], Kz [mD], phi [-], thickness [m]"""
PERMXY5 700.15 PERMZ5 700.15 PORO5 0.25 THIC2 20

"""Define the injection values""" 
"""injection time [d], time step size to write results [d], maximum time step [d], fluid (0 wetting, 1 non-wetting), injection rates [kg/day]"""
365 365 10 1 ${200000. / 6}
90 90 10 1 0
% for _,control in enumerate(schedule):
${tperiod} ${tperiod} .1 1 ${-1*qrate if control == 0 else qrate}
% endfor
730 730 10 1 ${-200000. / 6}