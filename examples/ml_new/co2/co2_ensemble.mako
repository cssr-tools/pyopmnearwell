"""Set the full path to the flow executable and flags"""
${FLOW} --ml-wi-filename="" --linear-solver-reduction=1e-5 --relaxed-max-pv-fraction=0 --ecl-enable-drift-compensation=0 --newton-max-iterations=50 --newton-min-iterations=5 --tolerance-mb=1e-7 --tolerance-wells=1e-5 --relaxed-well-flow-tol=1e-5 --use-multisegment-well=false --enable-tuning=true --enable-opm-rst-file=true --linear-solver=cprw --enable-well-operability-check=false --min-time-step-before-shutting-problematic-wells-in-days=1e-99

"""Set the model parameters"""
co2store no_disgas_no_diffusion #Model (co2store/h2store)
cake 60                         #Grid type (radial/cake/cartesian2d/cartesian/cave) and size (theta[in degrees]/theta[in degrees]/width[m]/anynumber(the y size is set equal to the x one))
100 ${HEIGHT}                   #Reservoir dimensions [m] (length and height)
400 ${NUM_LAYERS} 0             #Number of x- and z-cells [-] and exponential factor for the telescopic x-gridding (0 to use an equidistance partition)
${2*WELL_RADIUS} 1 0            #Well diameter [m], well transmiscibility (0 to use the computed one internally in Flow), and remove the smaller cells than the well diameter
${INIT_PRESSURE} ${INIT_TEMPERATURE}  0 #Pressure [Pa] on the top, uniform temperature [°], and initial phase in the reservoir (0 wetting, 1 non-wetting)
1e10 1                          #Pore volume multiplier on the boundary [-] (0 to use well producers instead) and deactivate cross flow within the wellbore (see XFLOW in OPM Manual)
0 5 10                          #Activate perforations [-], number of well perforations [-], and length [m]
${NUM_LAYERS} 0 0               #Number of layers [-] and hysteresis (1 to activate) and econ for the producer (for h2 models)
0 0 0 0 0 0 0                   #Initial salt concentration [kg/m3], salt solubility limit [kg/m3], and precipitated salt density [kg/m3] (for saltprec)
0                               #The function for the reservoir surface

"""Set the saturation functions"""
krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw             #Wetting rel perm saturation function [-]
krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn      #Non-wetting rel perm saturation function [-]
pec * ((sw - swi) / (1.0 - sni - swi)) ** (-(1.0 / npe))  #Capillary pressure saturation function [Pa]

"""Properties saturation functions"""
"""swi [-], sni [-], krn [-], krw [-], pec [Pa], nkrw [-], nkrn [-], npe [-], threshold cP evaluation, ignore swi for cP"""
SWI1 0. SNI5 0.0 KRW1 1 KRN1 1 PRE1 0 NKRW1 2 NKRN1 2 HNPE1 2 THRE2 1e-4 IGN1 0
SWI1 0. SNI5 0.0 KRW1 1 KRN1 1 PRE1 0 NKRW1 2 NKRN1 2 HNPE1 2 THRE2 1e-4 IGN1 0
SWI1 0. SNI5 0.0 KRW1 1 KRN1 1 PRE1 0 NKRW1 2 NKRN1 2 HNPE1 2 THRE2 1e-4 IGN1 0
SWI1 0. SNI5 0.0 KRW1 1 KRN1 1 PRE1 0 NKRW1 2 NKRN1 2 HNPE1 2 THRE2 1e-4 IGN1 0
SWI1 0. SNI5 0.0 KRW1 1 KRN1 1 PRE1 0 NKRW1 2 NKRN1 2 HNPE1 2 THRE2 1e-4 IGN1 0

"""Properties rock"""
"""Kxy [mD], Kz [mD], phi [-], thickness [m]"""
PERMXY1 ${PERMX_0} PERMZ1 ${PERMZ_by_PERMX_0 * PERMX_0} PORO1 0.25 THIC1 ${THICKNESS}
PERMXY1 ${PERMX_1} PERMZ1 ${PERMZ_by_PERMX_1 * PERMX_1} PORO1 0.25 THIC1 ${THICKNESS}
PERMXY1 ${PERMX_2} PERMZ1 ${PERMZ_by_PERMX_2 * PERMX_2} PORO1 0.25 THIC1 ${THICKNESS}
PERMXY1 ${PERMX_3} PERMZ1 ${PERMZ_by_PERMX_3 * PERMX_3} PORO1 0.25 THIC1 ${THICKNESS}
PERMXY1 ${PERMX_4} PERMZ1 ${PERMZ_by_PERMX_4 * PERMX_4} PORO1 0.25 THIC1 ${THICKNESS}

"""Define the injection values""" 
"""injection time [d], time step size to write results [d], maximum time step [d], injected fluid (0 wetting, 1 non-wetting), injection rates [kg/day]"""
1 1e-1 1e-1 1 ${INJECTION_RATE/6} # Divided by 6, since the model runs on a cake of 60°