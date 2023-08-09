"""Set the full path to the flow executable and flags"""
${flow} --linear-solver-reduction=1e-5 --relaxed-max-pv-fraction=0 --ecl-enable-drift-compensation=0 --newton-max-iterations=50 --newton-min-iterations=5 --tolerance-mb=1e-7 --tolerance-wells=1e-5 --relaxed-well-flow-tol=1e-5 --use-multisegment-well=false --enable-tuning=true --enable-opm-rst-file=true --linear-solver=cprw --enable-well-operability-check=false --min-time-step-before-shutting-problematic-wells-in-days=1e-99

"""Set the model parameters"""
co2store     #Model (co2store/h2store)
cake 36      #Grid type (radial/cake/cartesian2d/cartesian) and size (theta[in degrees]/theta[in degrees]/width[m]/anynumber(the y size is set equal to the x one))
500 40       #Reservoir dimensions [m] (Lenght and height)
100 40 0     #Number of x- and z-cells [-] and exponential factor for the telescopic x-gridding (0 to use an equidistance partition)
0.3 0 0      #Well diameter [m], well transmiscibility (0 to use the computed one internally in Flow), and remove the smaller cells than the well diameter
4e6 50  0    #Pressure [Pa] on the top, uniform temperature [°], and initial phase in the reservoir (0 wetting, 1 non-wetting)
1e3          #Pore volume multiplier on the boundary [-] (0 to use well producers instead)[-]
0 5 15       #Activate perforations [-], number of well perforations [-], and lenght [m]
4 0 0        #Number of layers [-], hysteresis (1 to activate), and econ for the producer (for h2 models)
10-10*mt.cos((2*mt.pi*x/100)) + 100*(x/500)**2 #The function for the reservoir surface

"""Set the saturation functions"""
krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw             #Wetting rel perm saturation function [-]
krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn      #Non-wetting rel perm saturation function [-]
pec * ((sw - swi) / (1.0 - sni - swi)) ** (-(1.0 / npe))  #Capillary pressure saturation function [Pa]

"""Properties saturation functions"""
"""swi [-], sni [-], krn [-], krw [-], pec [Pa], nkrw [-], nkrn [-], npe [-], threshold cP evaluation"""
SWI2  0.14 SNI2  0.1 KRW2  1 KRN2  1 PRE2  8655 NNKRW2 2 NNKRN2 2 HNPE2 2 THRE2  1e-4
SWI3  0.12 SNI3  0.1 KRW3  1 KRN3  1 PRE3  6120 NNKRW3 2 NNKRN3 2 HNPE3 2 THRE3  1e-4
SWI4  0.12 SNI4  0.1 KRW4  1 KRN4  1 PRE4  3871 NNKRW4 2 NNKRN4 2 HNPE4 2 THRE4  1e-4
SWI5  0.12 SNI5  0.1 KRW5  1 KRN5  1 PRE5  3060 NNKRW5 2 NNKRN5 2 HNPE5 2 THRE5  1e-4

"""Properties rock"""
"""Kxy [mD], Kz [mD], phi [-], thickness [m]"""
PERMXY2 101.324 PERMZ2 10.1324 PORO2 0.20 THIC2 10
PERMXY3 202.650 PERMZ3 20.2650 PORO3 0.20 THIC3 10
PERMXY4 506.625 PERMZ4 50.6625 PORO4 0.20 THIC4 10
PERMXY5 1013.25 PERMZ5 101.325 PORO5 0.25 THIC5 10

"""Define the injection values""" 
"""injection time [d], time step size to write results [d], maximum time step [d], fluid (0 wetting, 1 non-wetting), injection rates [kg/day]"""
${time} ${time} 10 1 34566.912
${time} ${time} 10 1 0
${time} ${time} 10 1 34566.912