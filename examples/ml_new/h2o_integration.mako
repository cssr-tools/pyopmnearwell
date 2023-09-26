"""Set the full path to the flow executable and flags"""
${flow} --ml-wi-filename="${ML_MODEL_PATH}" --linear-solver-reduction=1e-5 --relaxed-max-pv-fraction=0 --ecl-enable-drift-compensation=0 --newton-max-iterations=50 --newton-min-iterations=5 --tolerance-mb=1e-7 --tolerance-wells=1e-5 --relaxed-well-flow-tol=1e-5 --use-multisegment-well=false --enable-tuning=true --enable-opm-rst-file=true --linear-solver=cprw --enable-well-operability-check=false --min-time-step-before-shutting-problematic-wells-in-days=1e-99

"""Set the model parameters"""
co2store no_disgas_no_diffusion ${RUNNAME} #Model (co2store/h2store)
cartesian2d 0                   #Grid type (radial/cake/cartesian2d/cartesian/cave) and size (theta[in degrees]/theta[in degrees]/width[m]/anynumber(the y size is set equal to the x one))
${RESERVOIR_SIZE} 1             #Reservoir dimensions [m] (Length and height)
${GRID_SIZE} ${GRID_SIZE} 0     #Number of x- and z-cells [-] and exponential factor for the telescopic x-gridding (0 to use an equidistance partition)
${2*WELL_RADIUS} 1 0            #Well diameter [m], well transmiscibility (0 to use the computed one internally in Flow), and remove the smaller cells than the well diameter
${INIT_PRESSURE} ${INIT_TEMPERATURE}  0 #Pressure [Pa] on the top, uniform temperature [°], and initial phase in the reservoir (0 wetting, 1 non-wetting)
1e10 0                          #Pore volume multiplier on the boundary [-] (0 to use well producers instead) and deactivate cross flow within the wellbore (see XFLOW in OPM Manual)
0 5 10                          #Activate perforations [-], number of well perforations [-], and length [m]
1 0 0                           #Number of layers [-] and hysteresis (1 to activate) and econ for the producer (for h2 models)
0 0 0 0 0 0 0                   #Initial salt concentration [kg/m3], salt solubility limit [kg/m3], and precipitated salt density [kg/m3] (for saltprec)
0                               #The function for the reservoir surface

"""Set the saturation functions"""
krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw             #Wetting rel perm saturation function [-]
krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn      #Non-wetting rel perm saturation function [-]
pec * ((sw - swi) / (1.0 - sni - swi)) ** (-(1.0 / npe)) #Capillary pressure saturation function [Pa]

"""Properties saturation functions"""
"""swi [-], sni [-], krn [-], krw [-], pec [Pa], nkrw [-], nkrn [-], npe [-], threshold cP evaluation, ignore swi for cP"""
SWI5 0. SNI5 0.0 KRW5 1 KRN5 1 PRE5 0 NKRW5 2 NKRN5 2 HNPE5 2 THRE2 1e-4 IGN1 0

"""Properties rock"""
"""Kxy [mD], Kz [mD], phi [-], thickness [m]"""
PERMXY5 ${PERMX} PERMZ5 ${PERMZ} PORO5 0.25 THIC5 1

"""Define the injection values""" 
"""injection time [d], time step size to write results [d], maximum time step [d], injected fluid (0 wetting, 1 non-wetting), injection rates [kg/day]"""
10 1e-1 1e-1 0 ${INJECTION_RATE}