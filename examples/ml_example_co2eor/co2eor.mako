"""Set the full path to the flow executable and flags"""
${flow} --linear-solver=cprw --enable-opm-rst-file=true

"""Set the model parameters"""
co2eor       #Model (co2store/h2store)
cartesian2d 1 #Grid type (radial/cake/cartesian2d/cartesian) and size (theta[in degrees]/theta[in degrees]/width[m]/anynumber(the y size is set equal to the x one))
3500 100     #Reservoir dimensions [ft] (Lenght and height)
7 3 0        #Number of x- and z-cells [-] and exponential factor for the telescopic x-gridding (0 to use an equidistance partition)
0 0 0        #Well diameter [m], well transmiscibility (0 to use the computed one internally in Flow), and remove the smaller cells than the well diameter
0 0  0       #Pressure [Pa] on the top, uniform temperature [°], and initial phase in the reservoir (0 wetting, 1 non-wetting)
0            #Pore volume multiplier on the boundary [-] (0 to use well producers instead)[-]
0 0 0        #Activate perforations [-], number of well perforations [-], and lenght [m]
3 0 0        #Number of layers [-], hysteresis (1 to activate), and econ for the producer (for h2 models)
0 0 0        #Initial salt concentrationn [kg/m3], salt solubility limit [kg/m3], and precipitated salt density [kg/m3] (for saltprec)
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
PERMXY1 500 PERMZ1 50 PORO1 0.3 THIC1 20 NZ1 1
PERMXY2  50 PERMZ2 50 PORO2 0.3 THIC2 30 NZ2 1
PERMXY3 200 PERMZ3 25 PORO3 0.3 THIC3 50 NZ3 1

"""Define the injection values""" 
"""injection time [d], time step size to write results [d], maximum time step [d], fluid (0 wetting, 1 non-wetting), injection rates [stb/day]"""
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
30.25 30.25 1 1 ${rate}
30.5 30.5 1 0 45000
30.5 30.5 1 0 45000
30.25 30.25 1 0 45000
30.5 30.5 1 1 ${rate}
30.5 30.5 1 1 ${rate}
34.25 34.25 1 1 ${rate}