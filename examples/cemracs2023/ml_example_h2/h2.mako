#Set mpirun, the full path to the flow executable, and simulator flags (except --output-dir)
flow = "${flow} --relaxed-max-pv-fraction=0 --newton-min-iterations=1 --enable-opm-rst-file=true --enable-well-operability-check=false --min-time-step-before-shutting-problematic-wells-in-days=1e-99"

#Set the model parameters
model = "h2store" #Model: co2store, co2eor, foam, h2store, or saltprec
template = "okoroafor2023" #Template file (see src/pyopmnearwell/templates/)
grid = "cake" #Grid type: cake, radial, core, cartesian2d, coord2d, tensor2d, cartesian, cpg3d, coord3d, or tensor3d
adim = 36 #Grid cake/radial: theta [degrees]; core: input/output pipe length [m]; cartesian2d, coord2d, tensor2d: width[m]
xdim = 2500 #Length [m] (for cartesian/cpg3d/coord3d/tensor3d, Length=Width=2*xdim)
xcn = [25] #Number of x-cells [-]; coordinates for grid type coord2d/coord3d [m]; numbers of x-cells for grid type tensor2d/tensor3d [-]
diameter = 0.25 #Well diameter [m]
pressure = 40 #Pressure [Bar] on the top 
temperature = [50,50] #Top and bottom temperatures [C]
initialphase = 0 #Initial phase in the reservoir (0 wetting, 1 non-wetting)
pvmult = 1e6 #Pore volume multiplier on the boundary [-] (-1 to ignore; 0 to use well producers instead)
zxy = "300-300*mt.exp(-(x**2)/(2*500**2)) - 0*100*mt.exp(-((x-500)**2)/(2*100**2))" #The function for the reservoir surface
econ = 0.95 #For h2 models, econ for the producer

#Set the saturation functions
krw = "krw * ((sw - swi) / (1.0 - sni -swi)) ** nkrw"        #Wetting rel perm saturation function [-]
krn = "krn * ((1.0 - sw - sni) / (1.0 - sni - swi)) ** nkrn" #Non-wetting rel perm saturation function [-]
pcap = "pen * ((sw - swi) / (1.0 - swi)) ** (-(1.0 / npen))" #Capillary pressure saturation function [Bar]

#Properties sat functions: 1) swi [-], 2) sni [-], 3) krw [-], 4) krn [-], 5) pen [Bar], 6) nkrw [-],
#7) nkrn [-], 8) npen [-], 9) threshold cP evaluation, 10) ignore swi for cP? (sl* for cplog)
#11) npoints [-] (entry per layer, if hysteresis, additional entries per layer)
safu = [[0.1,0.1,0.8,0.2,4,4,3.5,1.2,1e-4,0,10000],[0.1,0.1,0.8,0.2,40,4,3.5,1.2,1e-4,0,10000],[0.1,0.1,0.8,0.2,4,4,3.5,1.2,1e-4,0,10000],[0.1,0.1,0.8,0.2,40,4,3.5,1.2,1e-4,0,10000]]

#Properties rock: 1) Kxy [mD], 2) Kz [mD], 3) phi [-], 4) thickness [m], and 5) no cells in the z dir [-] (entry per layer)
rock = [[10,10,0.1,10,5],[0.0001,0.0001,0.1,50,5],[700.15,700.15,0.25,20,5],[0.01,0.01,0.1,25,5]]

#Define the injection values (entry per change in the schedule): 
#1) injection time [d], 2) time step size to write results [d], 3) fluid (0 wetting, 1 non-wetting),
#4) injection rates [kg/day] (for h2store, 5) minimum BHP for producer [Bar]).
#If --enable-tuning=1, then last entry for TUNING values as described in the OPM manual.
inj = [[${time},${time},1,20000],
[90,10,1,0],
[7,7,1,-40000,3.6e1],
[7,7,1,40000],
[7,7,1,-40000,3.6e1],
[7,7,1,40000],
[7,7,1,-40000,3.6e1],
[7,7,1,40000],
[7,7,1,-40000,3.6e1],
[7,7,1,40000],
[7,7,1,-40000,3.6e1],
[7,7,1,40000]]