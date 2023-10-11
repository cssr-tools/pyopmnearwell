"""Set the full path to the flow executable and flags"""
${FLOW} --ml-wi-filename="" --linear-solver-reduction=1e-5 --relaxed-max-pv-fraction=0 --ecl-enable-drift-compensation=0 --newton-max-iterations=50 --newton-min-iterations=5 --tolerance-mb=1e-7 --tolerance-wells=1e-5 --relaxed-well-flow-tol=1e-5 --use-multisegment-well=false --enable-tuning=true --enable-opm-rst-file=true --linear-solver=cprw --enable-well-operability-check=false --min-time-step-before-shutting-problematic-wells-in-days=1e-99

"""Set the model parameters"""
co2store no_disgas_no_diffusion #Model (co2store/h2store)
cake 60                         #Grid type (radial/cake/cartesian2d/cartesian/cave) and size (theta[in degrees]/theta[in degrees]/width[m]/anynumber(the y size is set equal to the x one))
100 ${HEIGHT}                   #Reservoir dimensions [m] (length and height)
400 ${NUM_ZCELLS} 0             #Number of x- and z-cells [-] and exponential factor for the telescopic x-gridding (0 to use an equidistance partition)
${2*WELL_RADIUS} 1 0            #Well diameter [m], well transmiscibility (0 to use the computed one internally in Flow), and remove the smaller cells than the well diameter
${INIT_PRESSURE} ${INIT_TEMPERATURE}  0 #Pressure [Pa] on the top, uniform temperature [°], and initial phase in the reservoir (0 wetting, 1 non-wetting)
1e10 1                          #Pore volume multiplier on the boundary [-] (0 to use well producers instead) and deactivate cross flow within the wellbore (see XFLOW in OPM Manual)
0 5 10                          #Activate perforations [-], number of well perforations [-], and length [m]
${NUM_ZCELLS} 0 0               #Number of layers [-] and hysteresis (1 to activate) and econ for the producer (for h2 models)
0 0 0 0 0 0 0                   #Initial salt concentration [kg/m3], salt solubility limit [kg/m3], and precipitated salt density [kg/m3] (for saltprec)
0                               #The function for the reservoir surface

"""Set the saturation functions"""
krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw             #Wetting rel perm saturation function [-]
krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn      #Non-wetting rel perm saturation function [-]
pec * ((sw - swi) / (1.0 - sni - swi)) ** (-(1.0 / npe))  #Capillary pressure saturation function [Pa]

"""Properties saturation functions"""
"""swi [-], sni [-], krn [-], krw [-], pec [Pa], nkrw [-], nkrn [-], npe [-], threshold
cP evaluation, ignore swi for cP"""
% for i in range(NUM_ZCELLS):
SWI{i} 0. SNI{i} 0.0 KRW{i} 1 KRN{i} 1 PRE{i} 0 NKRW{i} 2 NKRN{i} 2 HNPE{i} 2 THRE{i} 1e-4 IGN{i} 0
% endfor

"""Properties rock"""
"""Kxy [mD], Kz [mD], phi [-], thickness [m]"""<% perms = [context.kwargs[f"PERM_{i}"] for i in range(NUM_ZCELLS)] %>
% for perm in perms:
PERMXY${loop.index} ${perm} PERMZ${loop.index} ${perm} PORO${loop.index} 0.25 THIC${loop.index} ${HEIGHT/NUM_ZCELLS}
% endfor

"""Define the injection values""" 
"""injection time [d], time step size to write results [d], maximum time step [d], injected fluid (0 wetting, 1 non-wetting), injection rates [kg/day]"""
1 1e-1 1e-1 0 ${INJECTION_RATE/6} # Divided by 6, since the model runs on a cake of 60°