#Set mpirun, the full path to the flow executable, and simulator flags (except --output-dir)
flow = "${FLOW} --relaxed-max-pv-fraction=0 --enable-opm-rst-file=true --newton-min-iterations=1"

#Set the model parameters
model = "co2store" #Model: co2store, co2eor, foam, h2store, or saltprec
template = "base" #Template file (see src/pyopmnearwell/templates/)
grid = "cake" #Grid type: cake, radial, core, cartesian2d, coord2d, tensor2d, cartesian, cpg3d, coord3d, or tensor3d
adim = 60 #Grid cake/radial: theta [degrees]; core: input/output pipe length [m]; cartesian2d, coord2d, tensor2d: width[m]
xdim = 400 #Length [m] (for cartesian/cpg3d/coord3d/tensor3d, Length=Width=2*xdim)
xcn = [10] #Number of x-cells [-]; coordinates for grid type coord2d/coord3d [m]; numbers of x-cells for grid type tensor2d/tensor3d [-]
xfac = 0 #Grid type radial/cake/cartesian2d/cartesian/cpg3d: exponential factor for the telescopic x-gridding (0 to use an equidistant partition)
diameter = 0.1 #Well diameter [m] 
pressure = ${PRESSURE} #Pressure [Bar] on the top 
temperature = [${TEMPERATURE},${TEMPERATURE}] #Top and bottom temperatures [C]
initialphase = 0 #Initial phase in the reservoir (0 wetting, 1 non-wetting)
pvmult = 1e5 #Pore volume multiplier on the boundary [-] (-1 to ignore; 0 to use well producers instead)
confact = 1 #Transmiscibility between well and reservoir [cPrm3/day/bars] (0 to use the computed one internally in Flow)
xflow = 1 #Deactivate cross flow within the wellbore (see XFLOW in OPM Manual)
removecells = 1 #Remove the smaller cells than the well diameter

#Set the saturation functions
krw = "krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw"        #Wetting rel perm saturation function [-]
krn = "krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn" #Non-wetting rel perm saturation function [-]
pcap = "pen * ((sw - swi) / (1.0 - swi)) ** (-(1.0 / npen))" #Capillary pressure saturation function [Bar]

#Properties sat functions: 1) swi [-], 2) sni [-], 3) krw [-], 4) krn [-], 5) pen [Bar], 6) nkrw [-],
#7) nkrn [-], 8) npen [-], 9) threshold cP evaluation, 10) ignore swi for cP? (sl* for cplog)
#11) npoints [-] (entry per layer, if hysteresis, additional entries per layer)
safu = [[0.14,0.1,1,1,8655e-5,2,2,2,1e-4,0,10000],
[0.12,0.1,1,1,6120e-5,2,2,2,1e-4,0,10000],
[0.12,0.1,1,1,3871e-5,2,2,2,1e-4,0,10000],
[0.12,0.1,1,1,3060e-5,2,2,2,1e-4,0,10000],
[0.14,0.2,1,1,8655e-5,2,3,2,1e-4,0,10000],
[0.12,0.2,1,1,6120e-5,2,3,2,1e-4,0,10000],
[0.12,0.2,1,1,3871e-5,2,3,2,1e-4,0,10000],
[0.12,0.2,1,1,3060e-5,2,3,2,1e-4,0,10000]]

#Properties rock: 1) Kxy [mD], 2) Kz [mD], 3) phi [-], 4) thickness [m], and 5) no cells in the z dir [-] (entry per layer)
rock = [[${PERMX},${PERMZ},0.25,1,1]]

#Define the injection values (entry per change in the schedule): 
#1) injection time [d], 2) time step size to write results [d], 3) maximum time step [d]
#4) fluid (0 wetting, 1 non-wetting), 5) injection rates [kg/day]
inj = [[10,0.1,0.1,1,${INJECTION_RATE}]]